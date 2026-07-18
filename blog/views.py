from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Categorie, Produit, Commande, LigneCommande
from .serializers import CategorieSerializer, ProduitSerializer, CommandeSerializer, LigneCommandeSerializer

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

class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer

    def perform_create(self, serializer):
        from .models import Commande
        derniere_commande = Commande.objects.last()
        serializer.save(commande = derniere_commande)

class AjouterLigneCommandeView(APIView):
    def post(self, request, pk):
        #Récupère la commande liée grace au pk de l'url
        commande = get_object_or_404(commande, id=pk)

        # Passe les données reçues au serialiseur
        serializer = LigneCommandeSerializer(data=request.data)

        if serializer.is_valid():
            #Sauvegarde la ligne en lui associant la commande parente
            serializer.save(commande=commande)
            return self.response(serializer.data, status=status.HTTP_201_BAD_CREATED)
        
        return Response(serializer.errors, status= status.HTTP_404_BAD_REQUEST)


   

