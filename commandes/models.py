from django.db import models
from django.conf import settings

class Panier(models.Model):
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='panier'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    def obtenir_total(self):
        return sum(article.obtenir_sous_total() for article in self.articles.all())


class ArticlePanier(models.Model):
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    produit = models.ForeignKey(
        'catalogue.Produit',
        on_delete=models.CASCADE
    )
    quantite = models.PositiveIntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def obtenir_sous_total(self):
        return self.quantite * self.produit.prix

    class Meta:
        unique_together = ['panier', 'produit']