from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('VENDOR', 'Vendor'),
        ('CUSTOMER', 'Customer')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # Préférences de notification
    notif_commandes = models.BooleanField(default=True)
    notif_promos = models.BooleanField(default=True)
    notif_favoris = models.BooleanField(default=True)
    notif_newsletter = models.BooleanField(default=True)


class SuiviBoutique(models.Model):

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boutiques_suivies'
    )

    boutique = models.ForeignKey(
        'boutiques.Boutique',
        on_delete=models.CASCADE,
        related_name='abonnes'
    )

    date_suivi = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'boutique'],
                name='unique_suivi_boutique'
            )
        ]

        ordering = ['-date_suivi']

    def __str__(self):
        return f"{self.utilisateur.username} suit {self.boutique.nom}"