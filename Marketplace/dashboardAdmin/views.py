from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from django.shortcuts import get_object_or_404
from boutiques.models import Boutique
from commandes.models import Commande
from produits.models import Produit
from django.db.models import Q
from .serializers import SerializerVendeursEnAttente, SerializerUtilisateursRecents
from .models import ParametresPlateforme
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


def has_admin_access(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return True
    return str(getattr(user, 'role', '')).upper() == 'ADMIN'


class AllowOptionsPermission(BasePermission):
    """
    Allow OPTIONS requests without authentication for CORS preflight.
    """
    def has_permission(self, request, _view):
        assert _view is not None
        logger.debug(f"AllowOptionsPermission check: method={request.method}, user={request.user}, is_auth={request.user.is_authenticated if request.user else 'NO USER'}")
        return request.method == 'OPTIONS' or bool(request.user and request.user.is_authenticated)


class VueParametresPlateforme(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        parametres, _ = ParametresPlateforme.objects.get_or_create(pk=1)
        return Response({
            'nom_plateforme': parametres.nom_plateforme,
            'email_contact': parametres.email_contact,
            'description': parametres.description,
            'validation_vendeurs': parametres.validation_vendeurs,
            'notifications_commandes': parametres.notifications_commandes,
            'notifications_vendeurs': parametres.notifications_vendeurs,
            'notifications_systeme': parametres.notifications_systeme,
        })

    def patch(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        parametres, _ = ParametresPlateforme.objects.get_or_create(pk=1)
        champs = [
            'nom_plateforme', 'email_contact', 'description',
            'validation_vendeurs', 'notifications_commandes',
            'notifications_vendeurs', 'notifications_systeme'
        ]
        for champ in champs:
            if champ in request.data:
                setattr(parametres, champ, request.data[champ])
        parametres.save()
        return self.get(request)


class VueCreationAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)

        username = str(request.data.get('username', '')).strip()
        email = str(request.data.get('email', '')).strip()
        password = str(request.data.get('password', ''))
        if not username or len(password) < 8:
            return Response({'detail': 'Nom d’utilisateur et mot de passe de 8 caractères minimum requis.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Ce nom d’utilisateur existe déjà.'}, status=400)

        admin = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='ADMIN'
        )
        return Response({
            'id': admin.id,
            'username': admin.username,
            'email': admin.email,
            'role': admin.role
        }, status=201)


class VueStatistiquesAdmin(APIView):

    permission_classes = [AllowOptionsPermission]

    def get(self, request):
        logger.debug(f"GET /stats called: user={request.user}, is_staff={request.user.is_staff}, is_auth={request.user.is_authenticated}")
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        today = timezone.now().date()
        start_month = today.replace(day=1)
        prev_month_end = start_month - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        periode = request.query_params.get('periode', 'ce_mois')
        if periode == 'aujourd_hui':
            periode_start = today
            periode_end = today
        elif periode == 'mois_precedent':
            periode_start = prev_month_start
            periode_end = prev_month_end
        elif periode == 'global':
            periode_start = None
            periode_end = None
        else:
            periode = 'ce_mois'
            periode_start = start_month
            periode_end = today

        utilisateurs_total = User.objects.count()
        nouveaux_utilisateurs_mois = User.objects.filter(date_joined__date__gte=start_month).count()
        vendeurs_actifs = Boutique.objects.filter(apprové=True).count()
        vendeurs_en_attente = Boutique.objects.filter(apprové=False).count()
        produits_total = Produit.objects.count()
        commandes = Commande.objects.all()
        if periode_start is not None:
            commandes = commandes.filter(
                date_creation__date__gte=periode_start,
                date_creation__date__lte=periode_end
            )

        commandes_total = commandes.count()
        commandes_du_jour = Commande.objects.filter(date_creation__date=today).count()
        commandes_ce_mois = commandes_total
        commandes_mois_precedent = Commande.objects.filter(date_creation__date__gte=prev_month_start, date_creation__date__lte=prev_month_end).count()

        def pct_change(curr, prev):
            if prev == 0:
                return None
            return round((curr - prev) / prev * 100, 1)

        commandes_change_pct = pct_change(commandes_ce_mois, commandes_mois_precedent)

        donnees = {
            'utilisateurs_total': utilisateurs_total,
            'nouveaux_utilisateurs_ce_mois': nouveaux_utilisateurs_mois,
            'vendeurs_actifs': vendeurs_actifs,
            'vendeurs_en_attente': vendeurs_en_attente,
            'produits_total': produits_total,
            'commandes_total': commandes_total,
            'commandes_du_jour': commandes_du_jour,
            'commandes_ce_mois': commandes_ce_mois,
            'commandes_mois_precedent': commandes_mois_precedent,
            'commandes_change_pct': commandes_change_pct,
        }

        return Response(donnees)


class VueVendeursEnAttente(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        vendeurs = Boutique.objects.filter(apprové=False)
        serializer = SerializerVendeursEnAttente(vendeurs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)

        boutique_id = request.data.get('boutique_id')
        approve = request.data.get('approve', True)
        boutique = Boutique.objects.filter(id=boutique_id).first()
        if boutique is None:
            return Response({'detail': 'Boutique introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        boutique.apprové = bool(approve)
        boutique.save(update_fields=['apprové'])
        return Response({'detail': 'Décision enregistrée.', 'approved': boutique.apprové})


class VueUtilisateursRecents(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)
        utilisateurs = User.objects.order_by('-date_joined')[:10]
        serializer = SerializerUtilisateursRecents(utilisateurs, many=True)
        return Response(serializer.data)


class VueExportCommandesAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only allow staff/admin users to export
        if not has_admin_access(request.user):
            return Response({'detail': 'Accès refusé.'}, status=403)

        commandes = Commande.objects.all().order_by('-date_creation')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="commandes_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'customer_username', 'customer_email', 'total_price', 'status', 'created_at', 'items'])

        for o in commandes:
            items = o.lignes.select_related('produit').all()
            items_summary = '; '.join([f"{it.produit.nom} x{it.quantite}" for it in items])
            writer.writerow([o.id, o.utilisateur.username, getattr(o.utilisateur, 'email', ''), str(o.montant_total), o.statut, o.date_creation.isoformat(), items_summary])

        return response
from rest_framework.generics import ListAPIView
from django.contrib.auth import get_user_model

User = get_user_model()

class VueListeUtilisateurs(ListAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = SerializerUtilisateursRecents

    def get_queryset(self):

        if not has_admin_access(self.request.user):
            return User.objects.none()

        recherche = self.request.GET.get("search")
        role = self.request.GET.get("role")
        statut = self.request.GET.get("statut")

        queryset = User.objects.all().order_by("-date_joined")

        if recherche:

            queryset = queryset.filter(
                Q(username__icontains=recherche)
            |   Q(first_name__icontains=recherche)
            |   Q(last_name__icontains=recherche)
            |   Q(email__icontains=recherche)
            |   Q(role__icontains=recherche)
            )

        if role:
            queryset = queryset.filter(
            role=role.upper()
            )

        if statut == "actif":
            queryset = queryset.filter(
            is_active=True
            )

        elif statut == "suspendu":
            queryset = queryset.filter(
                is_active=False
            )

        return queryset
from rest_framework.generics import RetrieveAPIView

class VueDetailUtilisateur(RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = SerializerUtilisateursRecents

    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):

        if not has_admin_access(request.user):
            return Response(
                {'detail': 'Accès refusé.'},
                status=403
            )

        return super().get(request, *args, **kwargs)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class VueGestionUtilisateur(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        if not has_admin_access(request.user):
            return Response(
                {"detail": "Accès refusé."},
                status=403
            )

        utilisateur = get_object_or_404(User, pk=pk)

        action = request.data.get("action")

        if action == "suspendre":

            utilisateur.is_active = False

        elif action == "reactiver":

            utilisateur.is_active = True

        else:

            return Response(
                {"detail": "Action invalide."},
                status=400
            )

        utilisateur.save(update_fields=["is_active"])

        return Response({
            "message": "Utilisateur mis à jour.",
            "is_active": utilisateur.is_active
        })

    def delete(self, request, pk):

        if not has_admin_access(request.user):
            return Response(
                {"detail": "Accès refusé."},
                status=403
            )

        utilisateur = get_object_or_404(User, pk=pk)

        utilisateur.delete()

        return Response({
            "message": "Utilisateur supprimé."
        })
class VueListeBoutiques(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not has_admin_access(request.user):
            return Response(
                {"detail": "Accès refusé"},
                status=403
            )

        boutiques = Boutique.objects.all().order_by("-id")

        serializer = SerializerVendeursEnAttente(
            boutiques,
            many=True
        )

        return Response(serializer.data) 

from django.shortcuts import get_object_or_404

class VueDetailBoutique(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        if not has_admin_access(request.user):
            return Response(
                {"detail": "Accès refusé"},
                status=403
            )

        boutique = get_object_or_404(Boutique, pk=pk)

        serializer = SerializerVendeursEnAttente(boutique)

        return Response(serializer.data)

    def patch(self, request, pk):

        if not has_admin_access(request.user):
            return Response(
                {"detail": "Accès refusé"},
                status=403
            )

        boutique = get_object_or_404(Boutique, pk=pk)
        approuve = request.data.get('apprové')

        if not isinstance(approuve, bool):
            return Response(
                {"detail": "La valeur apprové doit être booléenne."},
                status=400
            )

        boutique.apprové = approuve
        boutique.save(update_fields=['apprové'])

        return Response({
            "message": "Boutique mise à jour.",
            "apprové": boutique.apprové
        })