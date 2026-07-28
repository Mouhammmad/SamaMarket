from rest_framework import serializers
from .models import Boutique


class BoutiqueSerializer(serializers.ModelSerializer):
    total_produits = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Boutique
        fields = [
            'id',
            'nom',
            'description',
            'ville',
            'logo',
            'logo_url',
            'note',
            'followers',
            'ventes',
            'approuvé',
            'total_produits'
        ]

    def get_total_produits(self, obj):
        return obj.produits.count()

    def get_logo_url(self, obj):
        request = self.context.get('request')

        if obj.logo:
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url

        return None


class BoutiqueCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Boutique
        fields = [
            'id',
            'nom',
            'description',
            'ville',
            'logo'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        user = self.context["request"].user

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