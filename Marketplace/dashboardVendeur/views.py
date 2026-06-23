from rest_framework.views import APIView
from rest_framework.response import Response
from commandes.models import Commande
from produits.models import Produit

class VendeurDashboardStats(APIView):
    def get(self, request):

        boutique = request.utilisateur.boutique  # Supposons que chaque vendeur a une boutique liée à son compte

        # Logique pour calculer les statistiques du vendeur
        data = {
            "Revenu total": 100,  # Exemple de données
            "Commandes": Commande.objects.filter(boutique=boutique).count(),  # Exemple de données
            "Produits en vente": Produit.objects.filter(boutique=boutique).count(),  # Nombre de produits liés à la boutique du vendeur
            "rating": boutique.rating,  # Note de la boutique du vendeur
        }
        return Response(data)