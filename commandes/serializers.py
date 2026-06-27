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

from .models import Commande, LigneCommande, Paiement

class LigneCommandeSerializer(serializers.ModelSerializer):
    produit = ProduitResumSerializer(read_only=True)
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'quantite', 'prix_unitaire', 'sous_total']

    def get_sous_total(self, obj):
        return obj.calculer_sous_total()


class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    paiement = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = ['id', 'statut', 'montant_total', 'adresse_livraison', 'notes', 'lignes', 'paiement', 'date_creation']

    def get_paiement(self, obj):
        try:
            return PaiementSerializer(obj.paiement).data
        except:
            return None


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = ['id', 'montant', 'methode', 'statut', 'id_transaction', 'date_creation']