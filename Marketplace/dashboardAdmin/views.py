from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review


# Create your views here.
class AdminDashboardView(APIView):

    def get(self, request):
        return Response({
            "utilisateurs": 1284,
            "vendeurs": 87,
            "produits": 3420,
            "commandes_jour": 248
        })