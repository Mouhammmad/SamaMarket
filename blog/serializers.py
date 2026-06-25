from rest_framework import serializers 
from .models import Categorie, Produit, Commande, LigneCommande

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields= '__all__'


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields ='__all__'

class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'quantite', 'prix_unitaire']

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only= False)

    class Meta:
        model = Commande 
        fields = ['id','client', 'cree_le', 'statut', 'total', 'lignes'] 
      