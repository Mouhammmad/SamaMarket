from rest_framework import serializers
from .models import LigneCommande




class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = ['commande','id', 'produit', 'prix', 'quantite']