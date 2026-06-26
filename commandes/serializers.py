from rest_framework import serializers
from .models import Panier, ArticlePanier
from catalogue.models import Produit

class ProduitResumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image']


class ArticlePanierSerializer(serializers.ModelSerializer):
    produit = ProduitResumSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        source='produit',
        write_only=True
    )
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = ArticlePanier
        fields = ['id', 'produit', 'produit_id', 'quantite', 'sous_total', 'date_ajout']

    def get_sous_total(self, obj):
        return obj.obtenir_sous_total()


class PanierSerializer(serializers.ModelSerializer):
    articles = ArticlePanierSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'articles', 'total', 'date_mise_a_jour']

    def get_total(self, obj):
        return obj.obtenir_total()