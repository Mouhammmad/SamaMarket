from rest_framework import serializers

from samamarket.models import Product
from .models import Favorite


class ProductMiniSerializer(serializers.ModelSerializer):
    """Représentation légère du produit affichée dans la liste des favoris."""

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "old_price", "image",
            "category", "seller_name", "rating", "review_count",
            "badge", "in_stock",
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    """Utilisé pour GET /api/v1/favorites/ : item en lecture, imbriqué."""
    item = ProductMiniSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "item", "created_at"]


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """
    Utilisé pour POST /api/v1/favorites/ : { "item": <item_id> }.
    L'unicité (user, item) est vérifiée en base via unique_together ;
    on la traduit ici en erreur 400 explicite plutôt qu'en IntegrityError.
    """
    item = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Favorite
        fields = ["id", "item", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_item(self, value):
        user = self.context["request"].user
        if Favorite.objects.filter(user=user, item=value).exists():
            raise serializers.ValidationError("Cet élément est déjà dans vos favoris.")
        return value
