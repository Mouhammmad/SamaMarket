from django.conf import settings
from django.db import models

from boutiques.models import Boutique


class Conversation(models.Model):

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_client'
    )

    boutique = models.ForeignKey(
        Boutique,
        on_delete=models.CASCADE,
        related_name='conversations'
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    derniere_activite = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-derniere_activite']

    def __str__(self):
        return (
            f"{self.client.username} - "
            f"{self.boutique.nom}"
        )


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_envoyes'
    )

    contenu = models.TextField()

    lu = models.BooleanField(
        default=False
    )

    date_envoi = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['date_envoi']

    def __str__(self):
        return (
            f"Message de "
            f"{self.expediteur.username}"
        )