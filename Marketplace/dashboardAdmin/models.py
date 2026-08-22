from django.db import models


class ParametresPlateforme(models.Model):
    nom_plateforme = models.CharField(max_length=150, default='SAMA MARKET')
    email_contact = models.EmailField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    validation_vendeurs = models.BooleanField(default=True)
    notifications_commandes = models.BooleanField(default=True)
    notifications_vendeurs = models.BooleanField(default=True)
    notifications_systeme = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Paramètres de la plateforme'
        verbose_name_plural = 'Paramètres de la plateforme'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)