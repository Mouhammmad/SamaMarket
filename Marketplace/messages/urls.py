from django.urls import path

from .views import (
    ContacterBoutiqueView,
    MesConversationsView,
    ConversationDetailView,
    MessagesConversationView,
    EnvoyerMessageView,
)


urlpatterns = [

    # Contacter une boutique
    path(
        'boutiques/<int:boutique_id>/contacter/',
        ContacterBoutiqueView.as_view(),
        name='contacter-boutique'
    ),

    # Conversations du client connecté
    path(
        'conversations/',
        MesConversationsView.as_view(),
        name='mes-conversations'
    ),

    # Détail d'une conversation
    path(
        'conversations/<int:conversation_id>/',
        ConversationDetailView.as_view(),
        name='conversation-detail'
    ),

    # Messages d'une conversation
    path(
        'conversations/<int:conversation_id>/messages/',
        MessagesConversationView.as_view(),
        name='conversation-messages'
    ),

    # Envoyer un message
    path(
        'conversations/<int:conversation_id>/messages/envoyer/',
        EnvoyerMessageView.as_view(),
        name='envoyer-message'
    ),

]