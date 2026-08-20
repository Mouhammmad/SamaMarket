from rest_framework import serializers

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):

    expediteur_nom = serializers.CharField(
        source='expediteur.username',
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'expediteur',
            'expediteur_nom',
            'contenu',
            'lu',
            'date_envoi',
        ]

        read_only_fields = [
            'id',
            'expediteur',
            'lu',
            'date_envoi',
        ]


class ConversationSerializer(serializers.ModelSerializer):

    boutique_nom = serializers.CharField(
        source='boutique.nom',
        read_only=True
    )

    client_nom = serializers.CharField(
        source='client.username',
        read_only=True
    )

    boutique_logo = serializers.SerializerMethodField()

    dernier_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'client',
            'client_nom',
            'boutique',
            'boutique_nom',
            'boutique_logo',
            'date_creation',
            'derniere_activite',
            'dernier_message',
        ]

        read_only_fields = [
            'id',
            'client',
            'date_creation',
            'derniere_activite',
            'dernier_message',
        ]

    def get_boutique_logo(self, obj):

        request = self.context.get('request')

        if not obj.boutique.logo:
            return None

        url = obj.boutique.logo.url

        if request:
            return request.build_absolute_uri(url)

        return url

    def get_dernier_message(self, obj):

        message = obj.messages.order_by(
            '-date_envoi'
        ).first()

        if not message:
            return None

        return MessageSerializer(
            message,
            context=self.context
        ).data