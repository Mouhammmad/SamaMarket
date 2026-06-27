from rest_framework import serializers
from .models import Favori, Avis, Promotion, Produit


class ProduitResumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image']


class FavoriSerializer(serializers.ModelSerializer):
    produit = ProduitResumSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        source='produit',
        write_only=True
    )

    class Meta:
        model = Favori
        fields = ['id', 'produit', 'produit_id', 'date_ajout']


class AvisSerializer(serializers.ModelSerializer):
    utilisateur = serializers.StringRelatedField(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        source='produit',
        write_only=True
    )

    class Meta:
        model = Avis
        fields = ['id', 'utilisateur', 'produit_id', 'note', 'commentaire', 'est_approuve', 'date_creation']
        read_only_fields = ['est_approuve', 'date_creation']

    def validate_note(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


class PromotionSerializer(serializers.ModelSerializer):
    est_valide = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = ['id', 'code', 'taux_remise', 'type_remise', 'date_debut', 'date_fin', 'est_active', 'limite_usage', 'nombre_utilise', 'est_valide']

    def get_est_valide(self, obj):
        return obj.est_valide()