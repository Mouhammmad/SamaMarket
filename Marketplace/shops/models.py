from django.db import models
from django.conf import settings

# Create your models here.



class Boutique(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='boutique')
    nom = models.CharField(max_length=255,
                           default='')
    description = models.TextField()
    ville = models.CharField(max_length=255,
                            default='')
    logo = models.ImageField(upload_to='boutique_logos/',
                           default='default_logo.png')
    rating = models.FloatField(default=0)
    followers = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    