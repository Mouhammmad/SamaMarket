from rest_framework import serializers
from .models import Favori, Avis, Promotion, Produit, Categorie


class ProduitResumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image']


class ProduitSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    categorie = serializers.CharField(source='categorie.nom', read_only=True)

    categorie_id = serializers.PrimaryKeyRelatedField(
    queryset=Categorie.objects.all(),
    source='categorie',
    write_only=True
        )

    boutique_id = serializers.IntegerField(source='boutique.id', read_only=True)
    boutique = serializers.CharField(source='boutique.nom', read_only=True)

    class Meta:
        model = Produit
        fields = [
    'id',
    'nom',
    'description',
    'prix',
    'quantite_stock',
    'image',
    'image_url',

    'categorie',
    'categorie_id',

    'boutique_id',
    'boutique',

    'est_actif',
    'date_creation'
]

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
    boutique = serializers.CharField(source='boutique.nom', read_only=True)
    produits = ProduitResumSerializer(many=True, read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'code',
            'taux_remise',
            'type_remise',
            'date_debut',
            'date_fin',
            'est_active',
            'limite_usage',
            'nombre_utilise',
            'est_valide',
            'boutique',
            'produits'
        ]

    def get_est_valide(self, obj):
        return obj.est_valide()

class VendeurProduitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Produit
        fields = [
            'id',
            'categorie',
            'nom',
            'description',
            'prix',
            'quantite_stock',
            'image',
            'est_actif'
        ]
class ProduitCreateSerializer(serializers.ModelSerializer):
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie'
    )

    class Meta:
        model = Produit
        fields = [
            'id',
            'nom',
            'description',
            'prix',
            'quantite_stock',
            'image',
            'categorie_id',
            'est_actif'
        ]        