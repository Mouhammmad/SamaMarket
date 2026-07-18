from rest_framework import  viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Commande
from .serializers import LigneCommandeSerializer

#Vue personnalisée pour ajouter une ligne de commande à une commande existante via son PK
class AjouterLigneCommandeView(APIView):
    def post(self, request,pk):
        #1. On récupère la commande parente grace au <int:pk> de l'url
        # Si la commande n'existe pas, Django renvoie automatiquement une erreur 404
        commande = get_object_or_404(Commande, id=pk)

        # 2. On passe les données reçues (JSON) au sérialiseur de la ligne de commande 
        serializer = LigneCommandeSerializer(data=request.data)

        #3. On valide les données reçues (prix, quantité etc.)
        if serializer.is_value_fields_valid(): #ou serializer.is_valid()
            # 4. On enregistre la ligne en lui injectant manuellement la commande parente
            serializer.save(commande=commande)

            # Optionnel : Recalcul le total de la commande ici si nécessaire 

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # En cas d'erreur de validation (ex: quantité negative), on renvoie les erreurs
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    #serializer_class = CommandeSerializer

