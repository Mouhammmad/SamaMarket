from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Favori, Avis, Promotion, Produit, Categorie, ProduitImage, ProduitVariante
from .serializers import FavoriSerializer, AvisSerializer, PromotionSerializer, ProduitSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from boutiques.models import Boutique
from .serializers import ProduitCreateSerializer
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProduitVarianteSerializer, CategorieSerializer
from .pagination import ProduitPagination
from rest_framework.viewsets import ReadOnlyModelViewSet


from django.db.models import Avg, FloatField, Value
from django.db.models.functions import Coalesce
from django.db import transaction

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class CategorieViewSet(ReadOnlyModelViewSet):

    serializer_class = CategorieSerializer

    permission_classes = [AllowAny]

    queryset = Categorie.objects.prefetch_related(

        "sous_categories",

        "produits"

    )


from django.db.models import Q, Avg, Value
from django.db.models.functions import Coalesce

class ProduitFilter(django_filters.FilterSet):

    recherche = django_filters.CharFilter(
        method="filtrer_recherche"
    )

    categorie = django_filters.NumberFilter(
        field_name="categorie__id",
        lookup_expr="exact"
    )

    boutique = django_filters.CharFilter(
        field_name="boutique__nom",
        lookup_expr="icontains"
    )

    note = django_filters.NumberFilter(
        method="filtrer_note"
    )

    vendeurVerifie = django_filters.BooleanFilter(
        method="filtrer_vendeur_verifie"
    )

    prix_min = django_filters.NumberFilter(
        field_name="prix",
        lookup_expr="gte"
    )

    prix_max = django_filters.NumberFilter(
        field_name="prix",
        lookup_expr="lte"
    )

    disponible = django_filters.BooleanFilter(
        method="filtrer_disponible"
    )

    class Meta:

        model = Produit

        fields = []

    def filtrer_disponible(self, queryset, _name, value):
        assert _name is not None

        if value:

            return queryset.filter(
                quantite_stock__gt=0
            )

        return queryset.filter(
            quantite_stock=0
        )

    def filtrer_note(self, queryset, _name, value):
        assert _name is not None

        return queryset.filter(
            avis__note__gte=value,
            avis__est_approuve=True
        )

    def filtrer_vendeur_verifie(self, queryset, _name, value):
        assert _name is not None

        if value:
            return queryset.filter(
                boutique__apprové=True
            )

        return queryset

    def filtrer_recherche(self, queryset, _name, value):
        assert _name is not None

        return queryset.filter(

            Q(nom__icontains=value)

            |

            Q(description__icontains=value)

            |

            Q(categorie__nom__icontains=value)

            |

            Q(boutique__nom__icontains=value)

        )

class VueListeProduits(ListAPIView):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]
    pagination_class = ProduitPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProduitFilter
    search_fields = [

    "nom",

    "description",

    "categorie__nom",

    "boutique__nom"

]
    ordering_fields = [

    "prix",

    "date_creation",

    "nom",

    "nombre_vues",

    "quantite_stock"

]
    ordering = ['-date_creation']

    def get_queryset(self):
        return Produit.objects.filter(

    est_actif=True

).select_related(

    "categorie",

    "boutique"

).prefetch_related(

    "images",

    "variantes",

    "promotions",

    "avis"

)

class VueListeCategories(ListCreateAPIView):
    queryset = Categorie.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None
    serializer_class = CategorieSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            return CategorieSerializer(*args, **kwargs)
        from rest_framework import serializers
        class CategorieSerializer(serializers.ModelSerializer):
            class Meta:
                model = Categorie
                fields = ['id', 'nom', 'image']
        return CategorieSerializer(*args, **kwargs)


class VueDetailProduit(RetrieveAPIView):
    queryset = Produit.objects.filter(est_actif=True)
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]


from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class FavoriViewSet(ModelViewSet):

    serializer_class = FavoriSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Favori.objects.filter(

            utilisateur=self.request.user

        ).select_related("produit")

    def perform_create(self, serializer):

        serializer.save(

            utilisateur=self.request.user

        )

    @action(detail=False, methods=["post"])

    def toggle(self, request):

        produit = request.data.get("produit")

        favori = Favori.objects.filter(

            utilisateur=request.user,

            produit_id=produit

        ).first()

        if favori:

            favori.delete()

            return Response({

                "favori": False

            })

        Favori.objects.create(

            utilisateur=request.user,

            produit_id=produit

        )

        return Response({

            "favori": True

        })
class AvisViewSet(GenericViewSet):
    serializer_class = AvisSerializer

    def get_permissions(self):
        if self.action in ['list', 'avis_produit']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        produit_id = request.query_params.get('produit_id')
        est_vendeur = str(request.query_params.get('vendeur', '')).lower() == 'true'

        if est_vendeur:
            if not request.user.is_authenticated:
                return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
            role = getattr(request.user, 'role', '').upper()
            if role not in {'VENDOR', 'ADMIN'}:
                return Response({'detail': 'Accès réservé aux vendeurs.'}, status=status.HTTP_403_FORBIDDEN)
            avis = Avis.objects.all() if role == 'ADMIN' else Avis.objects.filter(
                produit__boutique__responsable=request.user
            )
            avis = avis.select_related('produit', 'utilisateur').order_by('-date_creation')
            serializer = AvisSerializer(avis, many=True, context={'request': request})
            return Response(serializer.data)

        if produit_id:
            avis = Avis.objects.filter(produit_id=produit_id, est_approuve=True)
        else:
            if not request.user.is_authenticated:
                return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
            avis = Avis.objects.filter(utilisateur=request.user)
        serializer = AvisSerializer(avis, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        serializer = AvisSerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            avis, created = Avis.objects.update_or_create(
                utilisateur=request.user,
                produit=produit,
                defaults={
                    'note': serializer.validated_data['note'],
                    'commentaire': serializer.validated_data.get('commentaire', ''),
                }
            )
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(AvisSerializer(avis, context={'request': request}).data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def avis_produit(self, request):
        produit_id = request.query_params.get('produit_id')
        avis = Avis.objects.filter(produit_id=produit_id, est_approuve=True)
        serializer = AvisSerializer(avis, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mes')
    def mes(self, request):
        """Retourne les avis de l'utilisateur connecté (tous états d'approbation)."""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        avis = Avis.objects.filter(utilisateur=request.user)
        serializer = AvisSerializer(avis, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def supprimer(self, request, pk=None):
        if getattr(request.user, 'role', '').upper() == 'ADMIN':
            avis = get_object_or_404(Avis, pk=pk)
            avis.delete()
            return Response({'message': 'Avis supprimé'})

        try:
            avis = Avis.objects.get(id=pk, utilisateur=request.user)
            avis.delete()
            return Response({'message': 'Avis supprimé'})
        except Avis.DoesNotExist:
            return Response({'erreur': 'Avis introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='moderation')
    def moderation(self, request, pk=None):
        if getattr(request.user, 'role', '').upper() != 'ADMIN':
            return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        avis = get_object_or_404(Avis, pk=pk)
        est_approuve = request.data.get('est_approuve')
        if not isinstance(est_approuve, bool):
            return Response({'detail': 'La valeur est_approuve doit être booléenne.'}, status=status.HTTP_400_BAD_REQUEST)

        avis.est_approuve = est_approuve
        avis.save(update_fields=['est_approuve'])
        return Response(AvisSerializer(avis, context={'request': request}).data)


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class PromotionViewSet(ModelViewSet):
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProduitPagination

    def get_queryset(self):
        try:
            boutique = self.request.user.boutique
        except Boutique.DoesNotExist:
            raise ValidationError(
                {"detail": "Aucune boutique associée."}
            )

        return Promotion.objects.filter(
            boutique=boutique
        ).prefetch_related("produits")

    def perform_create(self, serializer):
        try:
            boutique = self.request.user.boutique
        except Boutique.DoesNotExist:
            raise ValidationError(
                {"detail": "Aucune boutique associée."}
            )

        serializer.save(boutique=boutique)

class ProduitViewSet(ModelViewSet):
    """ViewSet public pour consulter les produits"""
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProduitFilter
    search_fields = ['nom', 'description', 'categorie__nom']
    ordering_fields = ['prix', 'date_creation', 'nom', 'note_moyenne']
    ordering = ['-date_creation']

    def get_queryset(self):
        return Produit.objects.filter(est_actif=True).select_related('categorie', 'boutique').annotate(
            note_moyenne=Coalesce(
                Avg('avis__note'),
                Value(0.0),
                output_field=FloatField()
            )
        )

    def list(self, request, *args, **kwargs):
        """Retourne les produits avec pagination et filtres"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Retourne les détails d'un produit"""
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):

        boutique = self.request.user.boutique

        serializer.save(boutique=boutique)

    @action(detail=True, methods=["get"])
    def similaires(self, request, _pk=None):
        assert _pk is not None

        produit = self.get_object()

        similaires = Produit.objects.filter(
            categorie=produit.categorie,
            est_actif=True
        ).exclude(
            id=produit.id
        )[:8]

        serializer = ProduitSerializer(
            similaires,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

class VendeurProduitViewSet(ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categorie']
    search_fields = ['nom', 'description']
    ordering_fields = ['prix', 'date_creation', 'nom']
    ordering = ['-date_creation']

    def get_boutique(self):
        try:
            boutique = self.request.user.boutique
        except Boutique.DoesNotExist:
            boutique = None

        if boutique is None:
            if getattr(self.request.user, 'role', '').upper() != 'VENDOR':
                raise ValidationError({'detail': 'Utilisateur sans boutique associée.'})

            boutique, _ = Boutique.objects.get_or_create(
                responsable=self.request.user,
                defaults={
                    'nom': f"Boutique de {self.request.user.first_name or self.request.user.username}",
                    'description': 'Boutique créée automatiquement',
                    'ville': 'À compléter'
                }
            )

        return boutique

    def get_queryset(self):
        boutique = self.get_boutique()
        return Produit.objects.filter(
            boutique=boutique
        ).select_related('categorie', 'boutique').order_by('-date_creation')

    def perform_create(self, serializer):

        boutique = self.get_boutique()

        serializer.save(
        boutique=boutique
        )
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProduitCreateSerializer
        return ProduitSerializer
class ProduitVarianteViewSet(ModelViewSet):

    serializer_class = ProduitVarianteSerializer

    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):

        return ProduitVariante.objects.filter(
            produit__boutique=self.get_boutique()
        )

    def get_boutique(self):

        try:
            return self.request.user.boutique

        except Boutique.DoesNotExist:

            raise ValidationError(
                {"detail": "Aucune boutique."}
            )

from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Promotion
from .serializers import PromotionSerializer


class VueListeOffres(ListAPIView):

    serializer_class = PromotionSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):

        aujourd_hui = timezone.now().date()

        return (
            Promotion.objects
            .filter(
                est_active=True,
                date_debut__lte=aujourd_hui,
                date_fin__gte=aujourd_hui
            )
            .select_related('boutique')
            .prefetch_related(
                'produits',
                'produits__images'
            )
            .order_by('-date_debut')
        )

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class AdminProduitViewSet(ModelViewSet):
    """
    Gestion des produits par l'administrateur.

    Contrairement au ViewSet public, l'admin peut voir
    les produits actifs ET inactifs.
    """

    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ProduitFilter

    search_fields = [
        'nom',
        'description',
        'categorie__nom',
        'boutique__nom',
    ]

    ordering_fields = [
        'prix',
        'date_creation',
        'nom',
        'quantite_stock',
        'est_actif',
    ]

    ordering = ['-date_creation']

    def get_queryset(self):

        user = self.request.user

        # Sécurité : seul l'administrateur
        # peut utiliser cet endpoint
        if getattr(user, 'role', '').upper() != 'ADMIN':
            raise PermissionDenied(
                'Accès réservé aux administrateurs.'
            )

        return Produit.objects.all() \
            .select_related(
                'categorie',
                'boutique'
            ) \
            .annotate(
                note_moyenne=Coalesce(
                    Avg('avis__note'),
                    Value(0.0),
                    output_field=FloatField()
                )
            )

    @action(detail=False, methods=['post'], url_path='nettoyer')
    def nettoyer(self, request):
        """Keep products 61-64 and remove all other product data."""
        from commandes.models import ArticlePanier, LigneCommande

        a_conserver = {61, 62, 63, 64}
        produits = Produit.objects.exclude(id__in=a_conserver)

        with transaction.atomic():
            lignes_panier = ArticlePanier.objects.filter(produit__in=produits).delete()[0]
            lignes_commandes = LigneCommande.objects.filter(produit__in=produits).delete()[0]
            produits_supprimes = produits.count()
            produits.delete()

        return Response({
            'produits_supprimes': produits_supprimes,
            'articles_panier_supprimes': lignes_panier,
            'lignes_commandes_supprimees': lignes_commandes,
            'produits_conserves': list(
                Produit.objects.filter(id__in=a_conserver)
                .values_list('id', 'nom')
                .order_by('id')
            ),
        })