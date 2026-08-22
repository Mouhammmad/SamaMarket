from decimal import Decimal
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import uuid
from django.db.models import Sum
from .models import Panier, ArticlePanier, Commande, LigneCommande, Paiement, Livraison, Notification
from .utils import _creer_notification
from produits.models import Promotion, Favori, Avis
from .serializers import (
    PanierSerializer, ArticlePanierSerializer,
    CommandeSerializer, LivraisonSerializer, NotificationSerializer
)
from produits.serializers import FavoriSerializer, AvisSerializer

logger = logging.getLogger(__name__)


def _calculer_reduction_promo(panier, code_promo):
    code_promo = (code_promo or '').strip()
    if not code_promo:
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Aucun code promo fourni',
            'code_promo': ''
        }

    aujourd_hui = timezone.now().date()
    promotion = Promotion.objects.filter(
        code__iexact=code_promo,
        est_active=True,
        date_debut__lte=aujourd_hui,
        date_fin__gte=aujourd_hui
    ).select_related('boutique').prefetch_related('produits').first()

    if not promotion:
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Code promo invalide',
            'code_promo': code_promo
        }

    if promotion.limite_usage > 0 and promotion.nombre_utilise >= promotion.limite_usage:
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Ce code promo n’est plus disponible',
            'code_promo': code_promo
        }

    articles = list(panier.articles.select_related('produit').all())
    if not articles:
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Votre panier est vide',
            'code_promo': code_promo
        }

    ids_produits = {article.produit_id for article in articles}
    if promotion.produits.exists() and not ids_produits.intersection(promotion.produits.values_list('id', flat=True)):
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Ce code promo ne s’applique pas à vos articles',
            'code_promo': code_promo
        }

    if promotion.boutique_id and not any(article.produit.boutique_id == promotion.boutique_id for article in articles):
        return {
            'applique': False,
            'reduction': Decimal('0.00'),
            'message': 'Ce code promo ne s’applique pas à votre boutique',
            'code_promo': code_promo
        }

    sous_total = panier.obtenir_total()
    if promotion.type_remise == 'pourcentage':
        reduction = (Decimal(promotion.taux_remise) / Decimal('100')) * sous_total
    else:
        reduction = min(Decimal(promotion.taux_remise), sous_total)

    return {
        'applique': True,
        'reduction': round(reduction, 2),
        'message': 'Code promo appliqué',
        'code_promo': code_promo,
        'promotion': promotion
    }


class PanierViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_panier(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        return panier

    @action(detail=False, methods=['get'])
    def mon_panier(self, request):
        panier = self.get_panier(request)
        serializer = PanierSerializer(panier, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        panier = self.get_panier(request)
        serializer = ArticlePanierSerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            quantite = serializer.validated_data.get('quantite', 1)
            article, created = ArticlePanier.objects.get_or_create(
                panier=panier,
                produit=produit
            )
            if not created:
                article.quantite += quantite
            else:
                article.quantite = quantite
            article.save()
            return Response(PanierSerializer(panier, context={'request': request}).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def modifier_quantite(self, request):
        panier = self.get_panier(request)
        article_id = request.data.get('article_id')
        quantite = request.data.get('quantite')
        try:
            article = ArticlePanier.objects.get(id=article_id, panier=panier)
            if quantite <= 0:
                article.delete()
            else:
                article.quantite = quantite
                article.save()
            return Response(PanierSerializer(panier, context={'request': request}).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def supprimer_article(self, request):
        panier = self.get_panier(request)
        article_id = request.data.get('article_id')
        try:
            article = ArticlePanier.objects.get(id=article_id, panier=panier)
            article.delete()
            return Response(PanierSerializer(panier, context={'request': request}).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def vider(self, request):
        panier = self.get_panier(request)
        panier.articles.all().delete()
        return Response({'message': 'Panier vidé'})

    @action(detail=False, methods=['post'])
    def appliquer_code_promo(self, request):
        panier = self.get_panier(request)
        code_promo = request.data.get('code_promo', '')
        result = _calculer_reduction_promo(panier, code_promo)

        if not result['applique']:
            return Response({'erreur': result['message']}, status=status.HTTP_400_BAD_REQUEST)

        sous_total = panier.obtenir_total()
        return Response({
            'message': result['message'],
            'code_promo': result['code_promo'],
            'reduction': float(result['reduction']),
            'sous_total': float(sous_total),
            'total': float(max(sous_total - result['reduction'], Decimal('0.00')))
        })


class CommandeViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Commande.objects.filter(utilisateur=self.request.user)

    @action(detail=False, methods=['post'])
    def valider_panier(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        if not panier.articles.exists():
            return Response({'erreur': 'Panier vide'}, status=status.HTTP_400_BAD_REQUEST)

        adresse = request.data.get('adresse_livraison')
        methode = request.data.get('methode_paiement')
        code_promo = request.data.get('code_promo', '')
        reduction_info = _calculer_reduction_promo(panier, code_promo)

        if code_promo and not reduction_info['applique']:
            return Response({'erreur': reduction_info['message']}, status=status.HTTP_400_BAD_REQUEST)

        if not adresse:
            return Response({'erreur': 'Adresse de livraison requise'}, status=status.HTTP_400_BAD_REQUEST)

        if methode not in ['wave', 'orange_money']:
            return Response({'erreur': 'Méthode de paiement invalide'}, status=status.HTTP_400_BAD_REQUEST)

        frais_livraison = request.data.get('prix_livraison', 0) or 0
        try:
            frais_livraison = Decimal(str(frais_livraison))
        except Exception:
            return Response({'erreur': 'Prix de livraison invalide'}, status=status.HTTP_400_BAD_REQUEST)

        commande = Commande.objects.create(
            utilisateur=request.user,
            adresse_livraison=adresse,
            sous_total=panier.obtenir_total(),
            boutique=panier.articles.first().produit.boutique,
            frais_livraison=frais_livraison,
            mode_livraison=request.data.get('mode_livraison', '') or '',
            reduction=reduction_info['reduction'],
        )

        for article in panier.articles.all():
            if article.quantite > article.produit.quantite_stock:
                return Response(
                    {'erreur': f"Stock insuffisant pour {article.produit.nom}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            LigneCommande.objects.create(
                commande=commande,
                produit=article.produit,
                quantite=article.quantite,
                prix_unitaire=article.produit.prix,
                total=article.quantite * article.produit.prix,
            )

            produit = article.produit

            produit.quantite_stock -= article.quantite

            produit.save(
                update_fields=["quantite_stock"]
            )

        Paiement.objects.create(
            commande=commande,
            montant=commande.montant_total,
            methode=methode,
        )

        if reduction_info['applique'] and reduction_info.get('promotion'):
            promotion = reduction_info['promotion']
            promotion.nombre_utilise = (promotion.nombre_utilise or 0) + 1
            promotion.save(update_fields=['nombre_utilise'])

        panier.articles.all().delete()

        _creer_notification(
            request.user,
            commande,
            f'Commande {commande.numero} reçue',
            f'Votre commande {commande.numero} a bien été créée et est en attente de traitement par le vendeur.',
            'commande'
        )

        if commande.boutique and getattr(commande.boutique, 'responsable', None):
            _creer_notification(
                commande.boutique.responsable,
                commande,
                f'Nouvelle commande {commande.numero}',
                f'Une nouvelle commande {commande.numero} est arrivée pour votre boutique.',
                'commande'
            )

        return Response({
            'message': 'Commande créée avec succès',
            'commande': CommandeSerializer(commande, context={'request': request}).data,
            'reduction': float(commande.reduction),
            'total': float(commande.montant_total),
        }, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def confirmer_paiement(self, request, pk=None):
        try:
            commande = Commande.objects.get(id=pk, utilisateur=request.user)
            paiement = commande.paiement
            id_transaction = request.data.get('id_transaction')

            if not id_transaction:
                return Response({'erreur': 'ID transaction requis'}, status=status.HTTP_400_BAD_REQUEST)

            paiement.id_transaction = id_transaction
            paiement.statut = 'complete'
            paiement.save()

            commande.statut = 'confirme'
            commande.save()

            return Response({
                'message': 'Paiement confirmé',
                'commande': CommandeSerializer(commande, context={'request': request}).data
            })
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def mes_commandes(self, request):
        assert request is not None
        commandes = self.get_queryset()
        serializer = CommandeSerializer(commandes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def notifications(self, request):
        notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_creation')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def marquer_toutes_lues(self, request):
        Notification.objects.filter(utilisateur=request.user, est_lu=False).update(est_lu=True)
        return Response({'message': 'Toutes les notifications ont été marquées comme lues'})

    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Retourne un résumé consolidé: notifications, commandes, favoris, avis, et promotions."""
        notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_creation')[:10]
        commandes = self.get_queryset()[:10]
        favoris = Favori.objects.filter(utilisateur=request.user)[:10]
        avis = Avis.objects.filter(utilisateur=request.user)[:10]

        # Récupérer les promotions actives sur les produits favoris
        produits_favoris = [f.produit_id for f in favoris]
        promotions_favoris = []
        if produits_favoris:
            from django.utils import timezone
            aujourd_hui = timezone.now().date()
            promotions_favoris = list(
                Promotion.objects.filter(
                    produits__id__in=produits_favoris,
                    est_active=True,
                    date_debut__lte=aujourd_hui,
                    date_fin__gte=aujourd_hui
                ).distinct()[:5]
            )

        return Response({
            'notifications': NotificationSerializer(notifications, many=True).data,
            'commandes': CommandeSerializer(commandes, many=True, context={'request': request}).data,
            'favoris': FavoriSerializer(favoris, many=True, context={'request': request}).data,
            'avis': AvisSerializer(avis, many=True, context={'request': request}).data,
            'promotions_favoris': [{'id': p.id, 'code': p.code, 'type_remise': p.type_remise, 'taux_remise': float(p.taux_remise), 'date_fin': p.date_fin.isoformat()} for p in promotions_favoris]
        })

class LivraisonViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def creer(self, request):
        commande_id = request.data.get('commande_id')
        try:
            commande = Commande.objects.get(id=commande_id, utilisateur=request.user)
            if commande.statut != 'confirme':
                return Response({'erreur': 'La commande doit être confirmée'}, status=status.HTTP_400_BAD_REQUEST)
            if hasattr(commande, 'livraison'):
                return Response({'erreur': 'Une livraison existe déjà pour cette commande'}, status=status.HTTP_400_BAD_REQUEST)

            livraison = Livraison.objects.create(
                commande=commande,
                adresse=commande.adresse_livraison,
                numero_suivi = (
                                "SAMA-"
                                 + uuid.uuid4().hex[:8].upper()
             ),      
                date_prevue=request.data.get('date_prevue')
            )
            commande.statut = 'expedie'
            commande.save()

            return Response(LivraisonSerializer(livraison).data, status=status.HTTP_201_CREATED)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def suivre(self, request):
        numero_suivi = request.query_params.get('numero_suivi')
        try:
            livraison = Livraison.objects.get(numero_suivi=numero_suivi)
            return Response(LivraisonSerializer(livraison).data)
        except Livraison.DoesNotExist:
            return Response({'erreur': 'Livraison introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def mettre_a_jour_statut(self, request, pk=None):
        try:
            livraison = Livraison.objects.get(id=pk)
            nouveau_statut = request.data.get('statut')
            if nouveau_statut not in dict(Livraison.STATUT_CHOICES):
                return Response({'erreur': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

            livraison.statut = nouveau_statut
            if nouveau_statut == 'livre':
                livraison.date_livraison = timezone.now()
                livraison.commande.statut = 'livre'
                livraison.commande.save()
            livraison.save()

            return Response(LivraisonSerializer(livraison).data)
        except Livraison.DoesNotExist:
            return Response({'erreur': 'Livraison introuvable'}, status=status.HTTP_404_NOT_FOUND)


class CommandeVendeurViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Commande.objects.filter(
            lignes__produit__boutique__responsable=self.request.user
        ).distinct()

    @action(detail=False, methods=['get'])
    def mes_commandes(self, request):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        commandes = self.get_queryset()
        serializer = CommandeSerializer(commandes, many=True, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)

        try:
            commande = Commande.objects.get(
                id=pk,
                lignes__produit__boutique__responsable=request.user
            )
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

        commande.delete()
        return Response({'message': 'Commande supprimée'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def mettre_a_jour_statut(self, request, pk=None):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            commande = Commande.objects.get(
                id=pk,
                lignes__produit__boutique__responsable=request.user
            )
            nouveau_statut = request.data.get('statut')
            if nouveau_statut not in dict(Commande.STATUT_CHOICES):
                return Response({'erreur': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

            commande.statut = nouveau_statut
            commande.save()

            if commande.utilisateur:
                if nouveau_statut == 'confirme':
                    titre = f'Commande {commande.numero} confirmée'
                    message = f'Votre commande {commande.numero} a été confirmée par le vendeur.'
                elif nouveau_statut == 'expedie':
                    titre = f'Commande {commande.numero} expédiée'
                    message = f'Votre commande {commande.numero} a été expédiée par le vendeur.'
                elif nouveau_statut == 'annule':
                    titre = f'Commande {commande.numero} annulée'
                    message = f'Votre commande {commande.numero} a été annulée par le vendeur.'
                else:
                    titre = f'Statut de la commande {commande.numero} mis à jour'
                    message = f'Le statut de votre commande {commande.numero} a été mis à jour en {commande.get_statut_display()}.'

                _creer_notification(
                    commande.utilisateur,
                    commande,
                    titre,
                    message,
                    'commande'
                )

            return Response(CommandeSerializer(commande, context={'request': request}).data)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def detail_commande(self, request, pk=None):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            commande = Commande.objects.get(
                id=pk,
                lignes__produit__boutique__responsable=request.user
            )
            return Response(CommandeSerializer(commande, context={'request': request}).data)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        assert request is not None
        commandes = self.get_queryset()

        total = commandes.count()

        en_attente = commandes.filter(
            statut='en_attente'
            ).count()

        confirmees = commandes.filter(
        statut='confirme'
        ).count()

        expediees = commandes.filter(
        statut='expedie'
        ).count()

        livrees = commandes.filter(
        statut='livre'
        ).count()

        annulees = commandes.filter(
        statut='annule'
        ).count()

        chiffre_affaires = commandes.aggregate(
            total=Sum("sous_total")
        )["total"] or 0

        return Response({

        "total_commandes": total,

        "en_attente": en_attente,

        "confirmees": confirmees,

        "expediees": expediees,

        "livrees": livrees,

        "annulees": annulees,

        "chiffre_affaires": chiffre_affaires

    })

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class AdminCommandeViewSet(ModelViewSet):
    """
    Gestion globale des commandes par l'administrateur.
    L'administrateur peut consulter toutes les commandes
    de la plateforme et modifier leur statut.
    """

    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    search_fields = [
        'numero',
        'utilisateur__first_name',
        'utilisateur__last_name',
        'utilisateur__username',
        'utilisateur__email',
    ]

    ordering_fields = [
        'date_creation',
        'sous_total',
        'statut',
    ]

    ordering = ['-date_creation']

    def get_queryset(self):

        user = self.request.user

        # Sécurité : seul l'administrateur
        # peut accéder à cette API
        if getattr(user, 'role', '').upper() != 'ADMIN':
            raise PermissionDenied(
                'Accès réservé aux administrateurs.'
            )

        return Commande.objects.all().select_related(
            'utilisateur',
            'boutique',
            'paiement'
        ).prefetch_related(
            'lignes',
            'lignes__produit'
        )

    def partial_update(self, request, *args, **kwargs):

        commande = self.get_object()

        nouveau_statut = request.data.get('statut')

        if nouveau_statut:

            statuts_valides = dict(
                Commande.STATUT_CHOICES
            )

            if nouveau_statut not in statuts_valides:
                return Response(
                    {
                        'erreur': 'Statut invalide.',
                        'statuts_valides': list(
                            statuts_valides.keys()
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            commande.statut = nouveau_statut
            commande.save(
                update_fields=['statut']
            )

            return Response(
                CommandeSerializer(
                    commande,
                    context={
                        'request': request
                    }
                ).data
            )

        return super().partial_update(
            request,
            *args,
            **kwargs
        )