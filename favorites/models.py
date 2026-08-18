from django.conf import settings
from django.db import models

# Modèle Product de l'app samamarket
from samamarket.models import Product


class Favorite(models.Model):
    """
    Modèle pivot User <-> Product.
    Un utilisateur ne peut mettre le même produit en favori qu'une seule fois
    (contrainte unique_together).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")
        ordering = ["-created_at"]
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"

    def __str__(self):
        return f"{self.user} -> {self.item}"
