from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('gestionnaire', 'Gestionnaire'),
        ('admin', 'Administrateur'),
    ]
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    photo_profil = models.ImageField(upload_to='profils/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"