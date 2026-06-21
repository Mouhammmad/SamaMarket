from django.db.models import Avg, Sum
from rest_framework.views import APIView
from rest_framework.response import Response

from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review


class VendorDashboardView(APIView):

    def get(self, request):

        product = Product.objects.first()

        if not product:
            return Response({
                "nombre_produits": 0,
                "nombre_commandes": 0,
                "revenu": 0,
                "note": 0
            })

        boutique = product.shop

        nombre_produits = Product.objects.filter(
            shop=boutique,
            active=True
        ).count()

        nombre_commandes = OrderItem.objects.filter(
            product__shop=boutique
        ).values('order').distinct().count()

        revenue = Order.objects.filter(
            status='DELIVERED'
        ).aggregate(
            total=Sum('total_price')
        )

        avg_rating = Review.objects.filter(
            product__shop=boutique
        ).aggregate(
            avg=Avg('rating')
        )

        return Response({
            "nombre_produits": nombre_produits,
            "nombre_commandes": nombre_commandes,
            "revenu": revenue["total"] or 0,
            "note": avg_rating["avg"] or 0
        })


class AdminDashboardView(APIView):

    def get(self, request):
        return Response({
            "utilisateurs": 1284,
            "vendeurs": 87,
            "produits": 3420,
            "commandes_jour": 248
        })