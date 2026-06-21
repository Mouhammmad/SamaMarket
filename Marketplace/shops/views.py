from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Boutique


class ShopListView(APIView):

    def get(self, request):

        boutiques = Boutique.objects.all()

        data = []

        for boutique in boutiques:
            data.append({
                "id": boutique.id,
                "name": boutique.nom,
                "description": boutique.description,
                "city": boutique.city,
                "verified": boutique.verified
            })

        return Response(data)