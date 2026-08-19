from django.db.models import Avg, Count
from rest_framework import serializers

from produits.models import Avis
from .models import Boutique


class BoutiqueSerializer(serializers.ModelSerializer):

    # ==========================================================
    # STATISTIQUES
    # ==========================================================

    total_produits = serializers.SerializerMethodField()
    nombre_produits = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()

    note = serializers.SerializerMethodField()

    repartition_notes = serializers.SerializerMethodField()

    categories = serializers.SerializerMethodField()
    categorie = serializers.SerializerMethodField()

    # ==========================================================
    # INFORMATIONS COMPLEMENTAIRES
    # ==========================================================

    verifie = serializers.SerializerMethodField()
    abonnes = serializers.SerializerMethodField()
    pays = serializers.SerializerMethodField()

    logo_url = serializers.SerializerMethodField()
    banniere_url = serializers.SerializerMethodField()

    # ==========================================================
    # DATE
    # ==========================================================

    membre_depuis = serializers.SerializerMethodField()

    class Meta:

        model = Boutique

        fields = [

            # --------------------------------------------------
            # IDENTITE
            # --------------------------------------------------

            'id',
            'nom',
            'description',
            'ville',

            # --------------------------------------------------
            # PAYS / IMAGES
            # --------------------------------------------------

            'pays',

            'logo',
            'logo_url',

            'banniere',
            'banniere_url',

            # --------------------------------------------------
            # CONTACT
            # --------------------------------------------------

            'telephone',
            'email',
            'whatsapp',

            # --------------------------------------------------
            # STATISTIQUES
            # --------------------------------------------------

            'note',
            'followers',
            'abonnes',
            'ventes',
            'apprové',
            'verifie',

            # --------------------------------------------------
            # CATEGORIES
            # --------------------------------------------------

            'categorie',
            'categories',

            # --------------------------------------------------
            # PRODUITS / AVIS
            # --------------------------------------------------

            'nombre_produits',
            'nombre_avis',
            'repartition_notes',
            'total_produits',

            # --------------------------------------------------
            # LIVRAISON
            # --------------------------------------------------

            'zones_livraison',
            'delai_livraison',
            'frais_livraison',

            # --------------------------------------------------
            # RETOURS
            # --------------------------------------------------

            'retours_acceptes',
            'delai_retour',

            # --------------------------------------------------
            # PAIEMENTS
            # --------------------------------------------------

            'wave_actif',
            'orange_money_actif',

            # --------------------------------------------------
            # NOTIFICATIONS
            # --------------------------------------------------

            'notifications_commandes',
            'notifications_avis',
            'notifications_messages',

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            'date_creation',
            'membre_depuis',
        ]

    # ==========================================================
    # PRODUITS
    # ==========================================================

    def _produits_boutique(self, obj):

        return obj.produits.select_related(
            'categorie'
        )

    def get_total_produits(self, obj):

        return self._produits_boutique(obj).count()

    def get_nombre_produits(self, obj):

        return self.get_total_produits(obj)

    # ==========================================================
    # AVIS
    # ==========================================================

    def get_nombre_avis(self, obj):

        return Avis.objects.filter(
            produit__boutique=obj,
            est_approuve=True
        ).count()

    def get_note(self, obj):

        moyenne = Avis.objects.filter(
            produit__boutique=obj,
            est_approuve=True
        ).aggregate(
            avg=Avg('note')
        )['avg']

        return round(
            float(moyenne),
            1
        ) if moyenne is not None else 0

    def get_repartition_notes(self, obj):

        counts = dict(
            Avis.objects.filter(
                produit__boutique=obj,
                est_approuve=True
            )
            .values_list('note')
            .annotate(
                total=Count('id')
            )
        )

        repartition = {
            note: counts.get(note, 0)
            for note in range(5, 0, -1)
        }

        return dict(
            sorted(
                repartition.items(),
                reverse=True
            )
        )

    # ==========================================================
    # CATEGORIES
    # ==========================================================

    def get_categories(self, obj):

        categories = []

        queryset = (
            obj.produits
            .exclude(categorie__isnull=True)
            .values_list(
                'categorie__id',
                'categorie__nom'
            )
            .distinct()
        )

        for categorie in queryset:

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

    # ==========================================================
    # VERIFICATION
    # ==========================================================

    def get_verifie(self, obj):

        return bool(
            obj.apprové
        )

    # ==========================================================
    # ABONNES
    # ==========================================================

    def get_abonnes(self, obj):

        return obj.followers

    # ==========================================================
    # PAYS
    # ==========================================================

    def get_pays(self, obj):

        return 'Sénégal'

    # ==========================================================
    # LOGO
    # ==========================================================

    def get_logo_url(self, obj):

        request = self.context.get('request')

        if obj.logo:

            if request:
                return request.build_absolute_uri(
                    obj.logo.url
                )

            return obj.logo.url

        return None

    # ==========================================================
    # BANNIERE
    # ==========================================================

    def get_banniere_url(self, obj):

        request = self.context.get('request')

        if obj.banniere:

            if request:
                return request.build_absolute_uri(
                    obj.banniere.url
                )

            return obj.banniere.url

        return None

    # ==========================================================
    # MEMBRE DEPUIS
    # ==========================================================

    def get_membre_depuis(self, obj):

        if not obj.date_creation:
            return None

        return obj.date_creation.year

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self, instance, validated_data):

        champs = [

            'nom',
            'description',
            'ville',

            'telephone',
            'email',
            'whatsapp',

            'zones_livraison',
            'delai_livraison',
            'frais_livraison',

            'retours_acceptes',
            'delai_retour',

            'wave_actif',
            'orange_money_actif',

            'notifications_commandes',
            'notifications_avis',
            'notifications_messages',

        ]

        for champ in champs:

            if champ in validated_data:

                setattr(
                    instance,
                    champ,
                    validated_data[champ]
                )

        # ------------------------------------------------------
        # LOGO
        # ------------------------------------------------------

        if 'logo' in validated_data:

            instance.logo = validated_data['logo']

        # ------------------------------------------------------
        # BANNIERE
        # ------------------------------------------------------

        if 'banniere' in validated_data:

            instance.banniere = validated_data['banniere']

        instance.save()

        return instance


class BoutiqueCreateSerializer(serializers.ModelSerializer):

    class Meta:

        model = Boutique

        fields = [

            'id',

            'nom',
            'description',
            'ville',

            'telephone',
            'email',
            'whatsapp',

            'logo',
            'banniere',

        ]

        read_only_fields = [
            'id'
        ]

    def validate(self, attrs):

        user = self.context['request'].user

        if self.instance is None:

            if Boutique.objects.filter(
                responsable=user
            ).exists():

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