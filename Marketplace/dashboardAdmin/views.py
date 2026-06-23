from django.contrib.auth import get_user_model
from shops.models import Boutique
#from produits.models import Product
#from commandes.models import Order
from rest_framework.views import APIView
from rest_framework.response import Response

class AdminDashboardStats(APIView):

    def get(self, request):

        data = {

            "utilisateurs": 0,  # Placeholder, replace with actual user count if needed

            "vendeurs": Boutique.objects.count(),

            "produits": 0,  # Placeholder, replace with actual product count if needed

            "commandes": 0  # Placeholder, replace with actual order count if needed
        }

        return Response(data)