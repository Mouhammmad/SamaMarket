from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    categorie = serializers.CharField(source='categorie.nom')
    boutique = serializers.CharField(source='boutique.nom')

    class Meta:
        model = Product
        fields = [
            'id',
            'nom',
            'description',
            'prix',
            'stock',
            'categorie',
            'boutique',
            'image'
        ]