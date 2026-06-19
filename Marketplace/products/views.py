from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product


class ProductListView(APIView):

    def get(self, request):

        products = Product.objects.filter(active=True)

        data = []

        for product in products:
            data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "category": product.category.name if product.category else None,
                "shop": product.shop.name,
                "image": product.image.url if product.image else None
            })

        return Response(data)