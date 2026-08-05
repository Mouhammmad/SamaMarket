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
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'role']
