from rest_framework import serializers
from .models import Favori, Avis, Promotion, Produit, Categorie, ProduitImage, ProduitVariante
from django.db.models import Avg
from django.utils import timezone

class ProduitResumSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image', 'image_url']

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

class ProduitImageSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProduitImage
        fields = [
            "id",
            "image",
            "image_url",
            "ordre"
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url

        return None

class ProduitVarianteSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()
    produit_id = serializers.PrimaryKeyRelatedField(

    queryset=Produit.objects.all(),

    source="produit",

    write_only=True

)

    class Meta:
        model = ProduitVariante

        fields = [

    "id",

    "produit_id",

    "nom",

    "valeur",

    "prix",

    "quantite_stock",

    "image",

    "image_url",

    "sku",

    "est_active"

]

    def get_image_url(self, obj):

        request = self.context.get("request")

        if obj.image:

            if request:
                return request.build_absolute_uri(obj.image.url)

            return obj.image.url

        return None

class ProduitSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    nombre_favoris = serializers.SerializerMethodField()

    nombre_avis = serializers.SerializerMethodField()

    note_moyenne = serializers.SerializerMethodField()

    promotion_active = serializers.SerializerMethodField()

    prix_promo = serializers.SerializerMethodField()
    images = ProduitImageSerializer( many=True, read_only=True )
    categorie = serializers.CharField(source='categorie.nom', read_only=True)

    categorie_id = serializers.PrimaryKeyRelatedField(
    queryset=Categorie.objects.all(),
    source='categorie',
    write_only=True
        )

    boutique_id = serializers.IntegerField(source='boutique.id', read_only=True)
    boutique = serializers.CharField(source='boutique.nom', read_only=True)
    variantes = ProduitVarianteSerializer(
    many=True,
    read_only=True
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
    'image_url',
    'images',
    "variantes",
    'categorie',
    'categorie_id',

    'boutique_id',
    'boutique',

    'est_actif',
    'date_creation',
    'nombre_favoris',

    'nombre_avis',

    'note_moyenne',

    'promotion_active',

    'prix_promo'
    
    
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
    def get_nombre_favoris(self, obj):
        return obj.favoris.count()
    def get_nombre_avis(self, obj):
        return obj.avis.filter(est_approuve=True).count()

    def get_note_moyenne(self, obj):

        moyenne = obj.avis.filter(
        est_approuve=True
        ).aggregate(
            Avg("note")
        )["note__avg"]
        return round(moyenne, 1) if moyenne else 0

    def get_promotion_active(self, obj):

        aujourd_hui = timezone.now().date()

        promotion = obj.promotions.filter(
        est_active=True,
        date_debut__lte=aujourd_hui,
        date_fin__gte=aujourd_hui
    ).first()

        if not promotion:
            return None

        if (
        promotion.limite_usage > 0 and
        promotion.nombre_utilise >= promotion.limite_usage
    ):
            return None

        return {
            "code": promotion.code,
            "type": promotion.type_remise,
            "valeur": promotion.taux_remise
        }

    def get_prix_promo(self, obj):

        if not self.get_promotion_active(obj):
            return obj.prix

        aujourd_hui = timezone.now().date()

        promotion = obj.promotions.filter(
            est_active=True,
            date_debut__lte=aujourd_hui,
            date_fin__gte=aujourd_hui
            ).first()

        if promotion.type_remise == "pourcentage":

        
            return round(
            obj.prix * (100 - promotion.taux_remise) / 100,
            2
        )

        return max(
        obj.prix - promotion.taux_remise,
        0
    )

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
    produits_ids = serializers.PrimaryKeyRelatedField(
    queryset=Produit.objects.all(),
    many=True,
    source="produits",
    write_only=True,
    required=False
)
    boutique = serializers.CharField(source='boutique.nom', read_only=True)
    produits = ProduitResumSerializer(many=True, read_only=True)
    

    produits_ids = serializers.PrimaryKeyRelatedField(
    queryset=Produit.objects.all(),
    many=True,
    source="produits",
    write_only=True
)

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

    'produits',

    'produits_ids'
]

    def get_est_valide(self, obj):
        return obj.est_valide()

    def create(self, validated_data):

        produits = validated_data.pop("produits", [])

        promotion = Promotion.objects.create(**validated_data)

        promotion.produits.set(produits)

        return promotion
    def update(self, instance, validated_data):

        produits = validated_data.pop("produits", None)

        for attr, value in validated_data.items():

            setattr(instance, attr, value)

        instance.save()

        if produits is not None:

            instance.produits.set(produits)

        return instance

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
from .models import ProduitImage

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

    def create(self, validated_data):
        request = self.context["request"]

        produit = Produit.objects.create(**validated_data)

        images = request.FILES.getlist("images")

        for index, image in enumerate(images):
            ProduitImage.objects.create(
                produit=produit,
                image=image,
                ordre=index
            )

        return produit
