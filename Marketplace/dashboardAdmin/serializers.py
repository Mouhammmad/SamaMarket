from django.contrib.auth import get_user_model
from rest_framework import serializers

from boutiques.models import Boutique

User = get_user_model()


class SerializerVendeursEnAttente(serializers.ModelSerializer):
    proprietaire = serializers.CharField(source='responsable.get_full_name', read_only=True)
    categorie = serializers.SerializerMethodField()
    email = serializers.CharField(source='responsable.email', read_only=True)
    
    class Meta:
        model = Boutique
        fields = ['id', 'nom', 'ville', 'note', 'apprové', 'proprietaire', 'categorie', 'email', 'description']
    
    def get_categorie(self, obj):
        categorie = getattr(obj, 'categorie', None)
        if categorie is None:
            return 'Général'
        return str(categorie)


class SerializerUtilisateursRecents(serializers.ModelSerializer):

    nom = serializers.SerializerMethodField()

    statut = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'nom',
            'email',
            'role',
            'phone',
            'date_joined',
            'is_active',
            'statut',
        ]

    def get_nom(self, obj):

        nom_complet = obj.get_full_name()

        if nom_complet:
            return nom_complet

        return obj.username

    def get_statut(self, obj):

        return 'Actif' if obj.is_active else 'Suspendu'