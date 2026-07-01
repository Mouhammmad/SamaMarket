from django.shortcuts import render
from rest_framework import viewsets
from Categorie.models import Categorie
from Categorie.serializers import CategorieSerializer


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer