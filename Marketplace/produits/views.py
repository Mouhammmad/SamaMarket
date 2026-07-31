from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Favori, Avis, Promotion, Produit, Categorie, ProduitImage, ProduitVariante
from .serializers import FavoriSerializer, AvisSerializer, PromotionSerializer, ProduitSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from boutiques.models import Boutique
from .serializers import ProduitCreateSerializer
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import ProduitVarianteSerializer

class ProduitFilter(django_filters.FilterSet):
    """Filtres avancés pour les produits"""
    prix_min = django_filters.NumberFilter(
        field_name='prix', 
        lookup_expr='gte',
        label='Prix minimum'
    )
    prix_max = django_filters.NumberFilter(
        field_name='prix', 
        lookup_expr='lte',
        label='Prix maximum'
    )
    categorie = django_filters.CharFilter(
        field_name='categorie__nom',
        lookup_expr='icontains',
        label='Catégorie'
    )
    boutique = django_filters.CharFilter(
        field_name='boutique__nom',
        lookup_expr='icontains',
        label='Boutique'
    )
    
    class Meta:
        model = Produit
        fields = ['categorie', 'boutique', 'prix_min', 'prix_max']


class VueListeProduits(ListAPIView):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProduitFilter
    search_fields = ['nom', 'description', 'categorie__nom']
    ordering_fields = ['prix', 'date_creation', 'nom']
    ordering = ['-date_creation']

    def get_queryset(self):
        return Produit.objects.filter(est_actif=True).select_related('categorie', 'boutique')

class VueListeCategories(ListAPIView):
    queryset = Categorie.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer(self, *args, **kwargs):
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


class FavoriViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favori.objects.filter(utilisateur=self.request.user)

    @action(detail=False, methods=['get'])
    def mes_favoris(self, request):
        favoris = self.get_queryset()
        serializer = FavoriSerializer(favoris, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        serializer = FavoriSerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            favori, created = Favori.objects.get_or_create(
                utilisateur=request.user,
                produit=produit
            )
            if not created:
                return Response({'message': 'Déjà dans les favoris'}, status=status.HTTP_200_OK)
            return Response(FavoriSerializer(favori).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def supprimer(self, request, pk=None):
        try:
            favori = Favori.objects.get(id=pk, utilisateur=request.user)
            favori.delete()
            return Response({'message': 'Retiré des favoris'})
        except Favori.DoesNotExist:
            return Response({'erreur': 'Favori introuvable'}, status=status.HTTP_404_NOT_FOUND)


class AvisViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        serializer = AvisSerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            if Avis.objects.filter(utilisateur=request.user, produit=produit).exists():
                return Response({'erreur': 'Vous avez déjà donné un avis sur ce produit'}, status=status.HTTP_400_BAD_REQUEST)
            avis = serializer.save(utilisateur=request.user)
            return Response(AvisSerializer(avis).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def avis_produit(self, request):
        produit_id = request.query_params.get('produit_id')
        avis = Avis.objects.filter(produit_id=produit_id, est_approuve=True)
        serializer = AvisSerializer(avis, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def supprimer(self, request, pk=None):
        try:
            avis = Avis.objects.get(id=pk, utilisateur=request.user)
            avis.delete()
            return Response({'message': 'Avis supprimé'})
        except Avis.DoesNotExist:
            return Response({'erreur': 'Avis introuvable'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class PromotionViewSet(ModelViewSet):
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]

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
    ordering_fields = ['prix', 'date_creation', 'nom']
    ordering = ['-date_creation']

    def get_queryset(self):
        return Produit.objects.filter(est_actif=True).select_related('categorie', 'boutique')

    def list(self, request, *args, **kwargs):
        """Retourne les produits avec pagination et filtres"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Retourne les détails d'un produit"""
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):

        boutique = self.request.user.boutique

        serializer.save(

        boutique=boutique

        )

class VendeurProduitViewSet(ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
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

            boutique, created = Boutique.objects.get_or_create(
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

        produit = serializer.save(
        boutique=boutique
        )

        images = self.request.FILES.getlist("images")

        if images:

            for index, image in enumerate(images):

                ProduitImage.objects.create(
                    produit=produit,
                    image=image,
                    ordre=index
                )

        elif self.request.FILES.get("image"):

            ProduitImage.objects.create(
            produit=produit,
            image=self.request.FILES["image"],
            ordre=0
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