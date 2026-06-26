from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Panier, ArticlePanier
from .serializers import PanierSerializer, ArticlePanierSerializer

class PanierViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_panier(self, request):
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        return panier

    @action(detail=False, methods=['get'])
    def mon_panier(self, request):
        panier = self.get_panier(request)
        serializer = PanierSerializer(panier)
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
            return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)
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
            return Response(PanierSerializer(panier).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def supprimer_article(self, request):
        panier = self.get_panier(request)
        article_id = request.data.get('article_id')
        try:
            article = ArticlePanier.objects.get(id=article_id, panier=panier)
            article.delete()
            return Response(PanierSerializer(panier).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def vider(self, request):
        panier = self.get_panier(request)
        panier.articles.all().delete()
        return Response({'message': 'Panier vidé'})