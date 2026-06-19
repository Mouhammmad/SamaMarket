from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review


class ReviewListView(APIView):

    def get(self, request):

        reviews = Review.objects.all()

        data = []

        for review in reviews:
            data.append({
                "id": review.id,
                "product": review.product.name,
                "customer": review.customer.email,
                "rating": review.rating,
                "comment": review.comment
            })

        return Response(data)