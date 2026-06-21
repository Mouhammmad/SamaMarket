from django.shortcuts import render

from rest_framework import viewsets
from .models import Categorie, Produit, Commande
from .serializers import CategorieSerializer, ProduitSerializer, CommandeSerializer


def home(request):
    return render(request, 'blog/home.html')

def about(request):
    return render(request,"blog/about.html")

def contact(request):
    return render(request, "blog/contact.html")


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer




   

