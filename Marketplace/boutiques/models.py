from django.conf import settings
from django.db import models


class Boutique(models.Model):

    responsable = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boutique'
    )

    # ==========================================================
    # INFORMATIONS PRINCIPALES
    # ==========================================================

    nom = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    ville = models.CharField(
        max_length=100,
        blank=True
    )

    logo = models.ImageField(
        upload_to='boutiques/',
        blank=True,
        null=True
    )

    banniere = models.ImageField(
        upload_to='boutiques/bannieres/',
        blank=True,
        null=True
    )

    # ==========================================================
    # COORDONNEES
    # ==========================================================

    telephone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    whatsapp = models.CharField(
        max_length=30,
        blank=True
    )

    # ==========================================================
    # INFORMATIONS COMMERCIALES
    # ==========================================================

    note = models.FloatField(
        default=0
    )

    followers = models.IntegerField(
        default=0
    )

    ventes = models.IntegerField(
        default=0
    )

    apprové = models.BooleanField(
        default=False
    )

    # ==========================================================
    # LIVRAISON
    # ==========================================================

    zones_livraison = models.TextField(
        blank=True,
        default=''
    )

    delai_livraison = models.CharField(
        max_length=100,
        blank=True,
        default='2-4 jours'
    )

    frais_livraison = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # ==========================================================
    # RETOURS
    # ==========================================================

    retours_acceptes = models.BooleanField(
        default=True
    )

    delai_retour = models.PositiveIntegerField(
        default=7
    )

    # ==========================================================
    # PAIEMENTS
    # ==========================================================

    wave_actif = models.BooleanField(
        default=True
    )

    orange_money_actif = models.BooleanField(
        default=True
    )

    # ==========================================================
    # NOTIFICATIONS
    # ==========================================================

    notifications_commandes = models.BooleanField(
        default=True
    )

    notifications_avis = models.BooleanField(
        default=True
    )

    notifications_messages = models.BooleanField(
        default=True
    )

    # ==========================================================
    # DATE
    # ==========================================================

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nom