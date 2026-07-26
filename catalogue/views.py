from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Favori, Avis, Promotion, Produit
from .serializers import FavoriSerializer, AvisSerializer, PromotionSerializer, ProduitResumSerializer


class ProduitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Produit.objects.filter(est_actif=True)
    serializer_class = ProduitResumSerializer
    permission_classes = [AllowAny]


class FavoriViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriSerializer

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
            favori, created = Favori.objects.get_or_create(utilisateur=request.user, produit=produit)
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
    serializer_class = AvisSerializer

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
    permission_classes = [IsAuthenticated]
    serializer_class = PromotionSerializer

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