from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shop


class ShopListView(APIView):

    def get(self, request):

        shops = Shop.objects.all()

        data = []

        for shop in shops:
            data.append({
                "id": shop.id,
                "name": shop.name,
                "description": shop.description,
                "city": shop.city,
                "verified": shop.verified
            })

        return Response(data)