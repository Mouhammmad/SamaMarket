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
                "products_count": 0,
                "orders_count": 0,
                "revenue": 0,
                "rating": 0
            })

        shop = product.shop

        products_count = Product.objects.filter(
            shop=shop,
            active=True
        ).count()

        orders_count = OrderItem.objects.filter(
            product__shop=shop
        ).values('order').distinct().count()

        revenue = Order.objects.filter(
            status='DELIVERED'
        ).aggregate(
            total=Sum('total_price')
        )

        avg_rating = Review.objects.filter(
            product__shop=shop
        ).aggregate(
            avg=Avg('rating')
        )

        return Response({
            "products_count": products_count,
            "orders_count": orders_count,
            "revenue": revenue["total"] or 0,
            "rating": avg_rating["avg"] or 0
        })


class AdminDashboardView(APIView):

    def get(self, request):
        return Response({
            "utilisateurs": 1284,
            "vendeurs": 87,
            "produits": 3420,
            "commandes_jour": 248
        })