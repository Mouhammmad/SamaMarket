from django.shortcuts import render
from rest_framework import viewsets
from .models import LigneCommande
from .serializers import  LigneCommandeSerializer

class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer
