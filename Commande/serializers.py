from rest_framework import serializers
from .models import Commande
from LigneCommande.serializers import LigneCommandeSerializer
from LigneCommande.models import  LigneCommande

class CommandeSerializer(serializers.ModelSerializer):
    ligne = LigneCommandeSerializer(many=True)

    class Meta:
        model = Commande
        fields = ['id', 'nom_client', 'email_client', 'statut', 'cree_le', 'ligne']

    def create(self, donnees_validees):
        # Extraction des articles pour enregistrer la commande principale d'abord
        donnees_ligne = donnees_validees.pop('ligne')
        commande = Commande.objects.create(**donnees_validees)
        
        # Enregistrement de chaque article lié à cette commande
        for donnees_ligne in donnees_ligne:
            LigneCommande.objects.create(commande=commande, **donnees_ligne)
            
        return commande
