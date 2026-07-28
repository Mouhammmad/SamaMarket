from django.contrib.auth import get_user_model
from rest_framework import serializers

from commandes.models import Commande
from produits.models import Categorie, Produit

User = get_user_model()


class SerializerCommandeVendeur(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    customer_username = serializers.CharField(source='utilisateur.username', read_only=True)
    total_price = serializers.DecimalField(source='montant_total', max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(source='statut', read_only=True)
    created_at = serializers.DateTimeField(source='date_creation', read_only=True)

    class Meta:
        model = Commande
        fields = ['id', 'customer_username', 'total_price', 'status', 'created_at', 'items']

    def get_items(self, obj):
        items = obj.lignes.select_related('produit').all()
        return [{'product': it.produit.nom, 'quantity': it.quantite, 'price': str(it.prix_unitaire)} for it in items]


class SerializerProduitVendeur(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    categorie = serializers.CharField(source='categorie.nom', read_only=True)

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'quantite_stock', 'est_actif', 'image_url', 'categorie']

    def get_image_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.image:
            try:
                url = obj.image.url
            except ValueError:
                return None
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class SerializerProduitCreateVendeur(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Produit
        fields = ['nom', 'description', 'prix', 'quantite_stock', 'est_actif', 'image', 'categorie_nom']

    def validate_prix(self, value):
        if value < 0:
            raise serializers.ValidationError('Le prix doit être positif.')
        return value

    def validate_quantite_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('La quantité doit être positive.')
        return value

    def create(self, validated_data):
        boutique = self.context.get('boutique')
        categorie_nom = validated_data.pop('categorie_nom', '').strip()
        if not boutique:
            raise serializers.ValidationError('Boutique introuvable pour l’utilisateur.')

        categorie = None
        if categorie_nom:
            categorie, _ = Categorie.objects.get_or_create(nom=categorie_nom)
        else:
            categorie = Categorie.objects.first()

        if categorie is None:
            raise serializers.ValidationError('Aucune catégorie disponible pour le produit.')

        return Produit.objects.create(boutique=boutique, categorie=categorie, **validated_data)
