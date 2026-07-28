from django.conf import settings
from django.db import models


class Boutique(models.Model):
    responsable = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='boutique')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    ville = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='boutiques/', blank=True, null=True)
    note = models.FloatField(default=0)
    followers = models.IntegerField(default=0)
    ventes = models.IntegerField(default=0)
    apprové = models.BooleanField(default=False)

    def __str__(self):
        return self.nom