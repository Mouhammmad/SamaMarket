from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from commandes.models import Commande, LigneCommande
from commandes.utils import _creer_notification
from produits.models import Produit

User = get_user_model()

from .serializers import SerializerCommandeVendeur, SerializerProduitVendeur, SerializerProduitCreateVendeur
from django.utils import timezone
from django.db.models import F
from datetime import date, timedelta

class VueVendeurBase(APIView):
    permission_classes = [IsAuthenticated]

    def get_boutique(self, request):
        return getattr(request.user, 'boutique', None)

    def get_date_range(self, period):
        """Retourne (start_date, end_date) basé sur la période"""
        today = timezone.now().date()
        
        if period == 'jour':
            start = today
            end = today + timedelta(days=1)
        elif period == 'semaine':
            start = today - timedelta(days=today.weekday())  # Lundi
            end = start + timedelta(days=7)
        elif period == 'mois':
            start = today.replace(day=1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1)
            else:
                end = date(today.year, today.month + 1, 1)
        elif period == 'annee':
            start = date(today.year, 1, 1)
            end = date(today.year + 1, 1, 1)
        else:  # 'tout'
            start = None
            end = None
        
        return start, end


class VueStatistiquesVendeur(VueVendeurBase):
    def get(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer la période depuis les query parameters
        period = request.query_params.get('period', 'mois')
        start_date, end_date = self.get_date_range(period)

        # Filtrer les lignes de commandes
        articles_query = LigneCommande.objects.filter(produit__boutique=boutique)
        
        if start_date and end_date:
            articles_query = articles_query.filter(
                commande__date_creation__date__gte=start_date,
                commande__date_creation__date__lt=end_date
            )

        revenus = articles_query.aggregate(total=Sum(F('prix_unitaire') * F('quantite')))['total'] or 0

        # Filtrer les commandes
        commandes_query = Commande.objects.filter(lignes__produit__boutique=boutique).distinct()
        
        if start_date and end_date:
            commandes_query = commandes_query.filter(
                date_creation__date__gte=start_date,
                date_creation__date__lt=end_date
            )

        commandes = commandes_query.count()

        donnees = {
            'revenue': float(revenus or 0),
            'orders': commandes,
            'products': Produit.objects.filter(boutique=boutique).count(),
            'rating': boutique.note,
        }
        # include boutique details for frontend (logo_url, nom...)
        try:
            logo_url = None
            if getattr(boutique, 'logo', None):
                try:
                    logo_rel = boutique.logo.url
                    logo_url = request.build_absolute_uri(logo_rel)
                except Exception:
                    logo_url = None
            donnees['boutique'] = {
                'id': boutique.id,
                'nom': boutique.nom,
                'logo_url': logo_url,
            }
        except Exception:
            donnees['boutique'] = None
        return Response(donnees)



class VueGraphiqueRevenus(VueVendeurBase):
    def get(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)
        # support ?period=jour|semaine|mois|annee|tout
        period = request.query_params.get('period', 'mois')
        start_date, end_date = self.get_date_range(period)

        data = []
        # if we have an explicit date range, bucket accordingly
        if start_date and end_date:
            if period == 'mois':
                today = timezone.now().date()
                # six months including current month
                def month_start(dt, months_ago):
                    y = dt.year
                    m = dt.month - months_ago
                    while m <= 0:
                        m += 12
                        y -= 1
                    return date(y, m, 1)

                cur = month_start(today, 5)
                while cur <= date(today.year, today.month, 1):
                    if cur.month == 12:
                        nxt = date(cur.year + 1, 1, 1)
                    else:
                        nxt = date(cur.year, cur.month + 1, 1)
                    items = LigneCommande.objects.filter(
                        produit__boutique=boutique,
                        commande__date_creation__date__gte=cur,
                        commande__date_creation__date__lt=nxt,
                    )
                    revenue = items.aggregate(total=Sum(F('prix_unitaire') * F('quantite')))['total'] or 0
                    data.append({'label': cur.strftime('%b %Y'), 'revenue': float(revenue)})
                    cur = nxt
            elif period in ('jour', 'semaine'):
                cur = start_date
                while cur < end_date:
                    nxt = cur + timedelta(days=1)
                    items = LigneCommande.objects.filter(
                        produit__boutique=boutique,
                        commande__date_creation__date__gte=cur,
                        commande__date_creation__date__lt=nxt,
                    )
                    revenue = items.aggregate(total=Sum(F('prix_unitaire') * F('quantite')))['total'] or 0
                    data.append({'label': cur.strftime('%Y-%m-%d'), 'revenue': float(revenue)})
                    cur = nxt
            else:
                cur = date(start_date.year, start_date.month, 1)
                while cur < end_date:
                    if cur.month == 12:
                        nxt = date(cur.year + 1, 1, 1)
                    else:
                        nxt = date(cur.year, cur.month + 1, 1)
                    items = LigneCommande.objects.filter(
                        produit__boutique=boutique,
                        commande__date_creation__date__gte=cur,
                        commande__date_creation__date__lt=nxt,
                    )
                    revenue = items.aggregate(total=Sum(F('prix_unitaire') * F('quantite')))['total'] or 0
                    data.append({'label': cur.strftime('%b %Y'), 'revenue': float(revenue)})
                    cur = nxt
            return Response(data)

        # fallback: previous behaviour (last 6 months)
        today = timezone.now().date()
        # helper to compute first day of month offset
        def month_start(dt, months_ago):
            y = dt.year
            m = dt.month - months_ago
            while m <= 0:
                m += 12
                y -= 1
            return date(y, m, 1)

        for i in range(5, -1, -1):
            start = month_start(today, i)
            # compute end as first day of next month
            if start.month == 12:
                end = date(start.year + 1, 1, 1)
            else:
                end = date(start.year, start.month + 1, 1)

            items = LigneCommande.objects.filter(produit__boutique=boutique, commande__date_creation__date__gte=start, commande__date_creation__date__lt=end)
            revenue = items.aggregate(total=Sum(F('prix_unitaire') * F('quantite')))['total'] or 0
            data.append({'label': start.strftime('%b %Y'), 'revenue': float(revenue)})

        return Response(data)


class VueVentesParCategorie(VueVendeurBase):
    def get(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)
        # support optional ?period=...
        period = request.query_params.get('period', 'tout')
        start_date, end_date = self.get_date_range(period)

        qs = LigneCommande.objects.filter(produit__boutique=boutique)
        if start_date and end_date:
            qs = qs.filter(commande__date_creation__date__gte=start_date, commande__date_creation__date__lt=end_date)

        qs = qs.values('produit__categorie__nom').annotate(
            sales_count=Sum('quantite'),
            revenue=Sum(F('prix_unitaire') * F('quantite'))
        )
        result = []
        for row in qs:
            result.append({
                'category': row['produit__categorie__nom'] or 'Autres',
                'sales': int(row['sales_count'] or 0),
                'revenue': float(row['revenue'] or 0),
            })
        return Response(result)


class VueCommandesRecents(VueVendeurBase):
    def get(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        commandes = Commande.objects.filter(lignes__produit__boutique=boutique).distinct().order_by('-date_creation')[:10]
        serializer = SerializerCommandeVendeur(commandes, many=True)
        return Response(serializer.data)


class VueProduitsVendeur(VueVendeurBase):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        produits = Produit.objects.filter(boutique=boutique)
        serializer = SerializerProduitVendeur(produits, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SerializerProduitCreateVendeur(data=request.data, context={'request': request, 'boutique': boutique})
        if serializer.is_valid():
            produit = serializer.save()
            return Response(SerializerProduitVendeur(produit, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VueMettreAJourStatutCommandeVendeur(VueVendeurBase):
    def patch(self, request, pk=None):
        role = getattr(request.user, 'role', None)
        if role not in {'VENDOR', 'gestionnaire', 'ADMIN'}:
            return Response({'detail': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)

        boutique = self.get_boutique(request)
        if boutique is None:
            return Response({'detail': 'Aucune boutique associée à cet utilisateur.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            commande = Commande.objects.get(id=pk, lignes__produit__boutique=boutique)
        except Commande.DoesNotExist:
            return Response({'detail': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

        nouveau_statut = request.data.get('statut') or request.data.get('status')
        if nouveau_statut not in dict(Commande.STATUT_CHOICES):
            return Response({'detail': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

        commande.statut = nouveau_statut
        commande.save()

        if commande.utilisateur:
            messages = {
                'en_attente': f'Votre commande {commande.numero} est en attente et sera traitée prochainement.',
                'confirme': f'Votre commande {commande.numero} a été confirmée par le vendeur.',
                'expedie': f'Votre commande {commande.numero} a été expédiée.',
                'livre': f'Votre commande {commande.numero} a été livrée.',
                'annule': f'Votre commande {commande.numero} a été annulée.',
            }
            _creer_notification(
                commande.utilisateur,
                commande,
                f'Statut de la commande {commande.numero}',
                messages.get(nouveau_statut, f'Le statut de votre commande {commande.numero} a été mis à jour.'),
                'commande'
            )

        return Response(SerializerCommandeVendeur(commande).data)