from django.db import models


class Categorie(models.Model):
    nom=models.CharField(max_length=100)
    description = models.TextField(blank=True)
    

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.nom
