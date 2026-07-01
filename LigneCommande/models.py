from django.db import models


class LigneCommande(models.Model):
    commande = models.ForeignKey('Commande.Commande', related_name='ligne', on_delete=models.CASCADE)
    produit = models.ForeignKey('Produit.Produit', on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
