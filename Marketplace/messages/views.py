from django.shortcuts import get_object_or_404
from django.db import models

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from boutiques.models import Boutique

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer
)


# ==========================================================
# CRÉER OU RÉCUPÉRER UNE CONVERSATION
# ==========================================================

class ContacterBoutiqueView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, boutique_id):

        boutique = get_object_or_404(
            Boutique,
            id=boutique_id
        )

        # Empêcher un vendeur de contacter sa propre boutique
        if boutique.responsable == request.user:

            return Response(
                {
                    'detail': 'Vous ne pouvez pas contacter votre propre boutique.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation, created = Conversation.objects.get_or_create(
            client=request.user,
            boutique=boutique
        )

        serializer = ConversationSerializer(
            conversation,
            context={
                'request': request
            }
        )

        return Response(
            {
                'conversation': serializer.data,
                'nouvelle': created
            },
            status=status.HTTP_201_CREATED if created
            else status.HTTP_200_OK
        )


# ==========================================================
# MES CONVERSATIONS
# ==========================================================

class MesConversationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        conversations = Conversation.objects.filter(
            models.Q(client=request.user) |
            models.Q(boutique__responsable=request.user)
        ).select_related(
            'boutique'
        )

        serializer = ConversationSerializer(
            conversations,
            many=True,
            context={
                'request': request
            }
        )

        return Response(serializer.data)


# ==========================================================
# UNE CONVERSATION
# ==========================================================

class ConversationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        if (
            conversation.client != request.user and
            conversation.boutique.responsable != request.user
        ):

            return Response(
                {
                    'detail': 'Vous n’avez pas accès à cette conversation.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ConversationSerializer(
            conversation,
            context={
                'request': request
            }
        )

        return Response(
            serializer.data
        )


# ==========================================================
# MESSAGES D'UNE CONVERSATION
# ==========================================================

class MessagesConversationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        if (
            conversation.client != request.user and
            conversation.boutique.responsable != request.user
        ):

            return Response(
                {
                    'detail': 'Vous n’avez pas accès à cette conversation.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        messages = conversation.messages.select_related(
            'expediteur'
        ).all()

        serializer = MessageSerializer(
            messages,
            many=True,
            context={
                'request': request
            }
        )

        return Response(
            serializer.data
        )


# ==========================================================
# ENVOYER UN MESSAGE
# ==========================================================

class EnvoyerMessageView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):

        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        if (
            conversation.client != request.user and
            conversation.boutique.responsable != request.user
        ):

            return Response(
                {
                    'detail': 'Vous n’avez pas accès à cette conversation.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        contenu = request.data.get(
            'contenu',
            ''
        ).strip()

        if not contenu:

            return Response(
                {
                    'detail': 'Le message ne peut pas être vide.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        message = Message.objects.create(
            conversation=conversation,
            expediteur=request.user,
            contenu=contenu
        )

        serializer = MessageSerializer(
            message,
            context={
                'request': request
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )