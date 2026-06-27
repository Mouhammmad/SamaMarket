from rest_framework import serializers
from django.contrib.auth import get_user_model

Utilisateur = get_user_model()

class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'telephone', 'adresse', 'photo_profil', 'role', 'date_joined']
        read_only_fields = ['id', 'role', 'date_joined']


class ModifierProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'telephone', 'adresse', 'photo_profil']

    def validate_email(self, value):
        utilisateur = self.context['request'].user
        if Utilisateur.objects.exclude(id=utilisateur.id).filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value


class ChangerMotDePasseSerializer(serializers.Serializer):
    ancien_mot_de_passe = serializers.CharField(required=True)
    nouveau_mot_de_passe = serializers.CharField(required=True, min_length=8)

    def validate_ancien_mot_de_passe(self, value):
        utilisateur = self.context['request'].user
        if not utilisateur.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value