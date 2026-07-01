from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Produit
from .serializers import ProduitSerializer

@api_view(['GET', 'POST'])
def produit(request):
    # 1. Gestion de la CRÉATION (Formulaire soumis)
    if request.method == 'POST':
        serializer = ProduitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # On peut retourner le produit créé avec un statut 201
            return Response(serializer.data, status=status.HTTP_01_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Gestion de l'AFFICHAGE (Chargement de la page)
    elif request.method == 'GET':
        produits = Produit.objects.all()
        serializer = ProduitSerializer(produits, many=True)
        return Response(serializer.data)
