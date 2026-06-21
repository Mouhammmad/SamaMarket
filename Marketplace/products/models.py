from django.db import models
from shops.models import Boutique
# Create your models here.
class Category(models.Model):

    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Product(models.Model):

    boutique = models.ForeignKey(
        Boutique,
        on_delete=models.CASCADE,
        related_name='products'
    )

    categorie = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    nom = models.CharField(max_length=200)

    description = models.TextField()

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField()

    image = models.ImageField(upload_to='products/')

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)    