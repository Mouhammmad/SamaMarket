from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from samamarket.models import Product
from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer


class FavoriteListCreateView(APIView):
    """
    GET  /api/v1/favorites/  -> liste les favoris de l'utilisateur connecté.
    POST /api/v1/favorites/  -> { "item": <item_id> } ajoute un favori.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = (
            Favorite.objects.filter(user=request.user)
            .select_related("item")
        )
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FavoriteCreateSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                favorite = serializer.save(user=request.user)
        except IntegrityError:
            # Filet de sécurité si deux requêtes concurrentes passent la
            # validation en même temps (contrainte unique_together en base).
            # Le sous-bloc atomic() isole l'échec pour ne pas casser le
            # reste de la transaction de la requête si ATOMIC_REQUESTS=True.
            return Response(
                {"item": ["Cet élément est déjà dans vos favoris."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            FavoriteCreateSerializer(favorite).data,
            status=status.HTTP_201_CREATED,
        )


class FavoriteDestroyView(APIView):
    """
    DELETE /api/v1/favorites/<item_id>/
    Supprime le favori de l'élément <item_id> pour l'utilisateur connecté.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        # 404 si le produit lui-même n'existe pas, ou s'il n'est pas
        # dans les favoris de l'utilisateur connecté.
        item = get_object_or_404(Product, id=item_id)
        favorite = Favorite.objects.filter(user=request.user, item=item).first()
        if not favorite:
            return Response(
                {"detail": "Cet élément n'est pas dans vos favoris."},
                status=status.HTTP_404_NOT_FOUND,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
