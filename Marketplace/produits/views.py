from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .models import Favori, Avis, Promotion, Produit, Categorie
from .serializers import FavoriSerializer, AvisSerializer, PromotionSerializer, ProduitSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from boutiques.models import Boutique
from .serializers import ProduitCreateSerializer

class VueListeProduits(ListAPIView):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Produit.objects.filter(est_actif=True).order_by('-date_creation')

        recherche = self.request.query_params.get('search')

        if recherche:
            queryset = queryset.filter(nom__icontains=recherche)

        return queryset

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


class PromotionViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        today = timezone.now().date()
        return Promotion.objects.filter(
            est_active=True,
            date_debut__lte=today,
            date_fin__gte=today
        )

    def list(self, request):
        promotions = self.get_queryset()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def appliquer(self, request):
        code = request.data.get('code')
        try:
            promotion = Promotion.objects.get(code=code)
            if not promotion.est_valide():
                return Response({'erreur': 'Code promo invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(PromotionSerializer(promotion).data)
        except Promotion.DoesNotExist:
            return Response({'erreur': 'Code promo introuvable'}, status=status.HTTP_404_NOT_FOUND)

class ProduitViewSet(ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Produit.objects.filter(
            boutique__responsable=self.request.user
        ).order_by('-date_creation')

    def perform_create(self, serializer):
        boutique = Boutique.objects.get(
            responsable=self.request.user
        )

        serializer.save(
    boutique=boutique,
    est_actif=True
)
class VendeurProduitViewSet(ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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
        ).order_by('-date_creation')

    def perform_create(self, serializer):
        boutique = self.get_boutique()
        serializer.save(boutique=boutique)
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProduitCreateSerializer
        return ProduitSerializer