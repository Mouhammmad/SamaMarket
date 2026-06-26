from django.db import models
from django.conf import settings

class Boutique(models.Model):
    gestionnaire = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boutique'
    )
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='boutiques/', blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    est_active = models.BooleanField(default=True)
    est_validee = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom