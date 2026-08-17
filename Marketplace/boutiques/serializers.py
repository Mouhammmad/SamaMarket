from django.db.models import Avg, Count
from rest_framework import serializers

from produits.models import Avis
from .models import Boutique


class BoutiqueSerializer(serializers.ModelSerializer):
    total_produits = serializers.SerializerMethodField()
    nombre_produits = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    repartition_notes = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    categorie = serializers.SerializerMethodField()
    verifie = serializers.SerializerMethodField()
    abonnes = serializers.SerializerMethodField()
    pays = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    banniere_url = serializers.SerializerMethodField()

    class Meta:
        model = Boutique
        fields = [
            'id',
            'nom',
            'description',
            'ville',
            'pays',
            'logo',
            'logo_url',
            'banniere',
            'banniere_url',
            'note',
            'followers',
            'abonnes',
            'ventes',
            'apprové',
            'verifie',
            'categorie',
            'categories',
            'nombre_produits',
            'nombre_avis',
            'repartition_notes',
            'total_produits'
        ]

    def _produits_boutique(self, obj):
        return obj.produits.select_related('categorie')

    def get_total_produits(self, obj):
        return self._produits_boutique(obj).count()

    def get_nombre_produits(self, obj):
        return self.get_total_produits(obj)

    def get_nombre_avis(self, obj):
        return Avis.objects.filter(produit__boutique=obj, est_approuve=True).count()

    def get_note(self, obj):
        moyenne = Avis.objects.filter(produit__boutique=obj, est_approuve=True).aggregate(avg=Avg('note'))['avg']
        return round(float(moyenne), 1) if moyenne is not None else 0

    def get_repartition_notes(self, obj):
        counts = dict(
            Avis.objects.filter(produit__boutique=obj, est_approuve=True)
            .values_list('note')
            .annotate(total=Count('id'))
        )
        repartition = {note: counts.get(note, 0) for note in range(5, 0, -1)}
        return dict(sorted(repartition.items(), reverse=True))

    def get_categories(self, obj):
        categories = []
        for categorie in obj.produits.exclude(categorie__isnull=True).values_list('categorie__id', 'categorie__nom').distinct():
            categories.append({
                'id': categorie[0],
                'nom': categorie[1]
            })
        return categories

    def get_categorie(self, obj):
        categories = self.get_categories(obj)
        if not categories:
            return ''
        return categories[0]['nom']

    def get_verifie(self, obj):
        return bool(obj.apprové)

    def get_abonnes(self, obj):
        return obj.followers

    def get_pays(self, obj):
        return getattr(obj, 'pays', '') or 'Sénégal'

    def get_logo_url(self, obj):
        request = self.context.get('request')

        if obj.logo:
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url

        return None

    def update(self, instance, validated_data):
        instance.nom = validated_data.get("nom", instance.nom)
        instance.description = validated_data.get(
            "description",
            instance.description
        )
        instance.ville = validated_data.get(
            "ville",
            instance.ville
        )

        if "logo" in validated_data:
            instance.logo = validated_data["logo"]

        instance.save()

        return instance

    def get_banniere_url(self, obj):
        request = self.context.get('request')

        if obj.banniere:
            if request:
                return request.build_absolute_uri(obj.banniere.url)
            return obj.banniere.url

        return None

class BoutiqueCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Boutique
        fields = [
            'id',
            'nom',
            'description',
            'ville',
            'logo',
            'banniere'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
            user = self.context["request"].user

            if self.instance is None:
                if Boutique.objects.filter(responsable=user).exists():
                    raise serializers.ValidationError(
                "Vous possédez déjà une boutique."
            )

            return attrs
    
    def create(self, validated_data):
        request = self.context['request']

        return Boutique.objects.create(
            responsable=request.user,
            **validated_data
        )
