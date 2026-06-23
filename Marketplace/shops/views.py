from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Boutique
from .serializers import BoutiqueSerializer
from rest_framework import generics

# une vue pour récupérer la liste de toutes les boutiques
class BoutiqueView(generics.ListAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer

# une vue pour récupérer les détails d'une boutique spécifique


class BoutiqueDetailView(generics.RetrieveAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer

# une vue pour récupérer les produits d'une boutique spécifique
class BoutiqueProduitsView(generics.ListAPIView):
    serializer_class = ProduitSerializer

    def get_queryset(self):
        return Produit.objects.filter(boutique_id=self.kwargs['pk'])

# une vue pour récupérer les avis d'une boutique spécifique
class BoutiqueAvisView(generics.ListAPIView):
    serializer_class = AvisSerializer

    def get_queryset(self):
        return Avis.objects.filter(boutique_id=self.kwargs['pk'])