from rest_framework import serializers
from .models import  Boutique

class BoutiqueSerializer(serializers.ModelSerializer):
    total_produits = serializers.SerializerMethodField()
    class Meta:
        model = Boutique
        fields = ['id',
                  'nom',
                  'description',
                  'ville',
                  'logo',  
                  'rating', 
                  'followers', 
                  'sales'
                  'sales',
                  'total_produits'
                  ]
    def get_total_produits(self, obj):
        return obj.produit_set.count()    