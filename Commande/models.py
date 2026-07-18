from django.db import models
from django.contrib.auth.models import User
from blog.models import Commande, Produit

class Commande(models.Model):
    STATUT_CHOICES =[
        ('En attente', 'En attente'),
        ('Payée', 'Payée'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée')
    ]
    #L'utilisateur "User" de django sert ici de client
    client= models.ForeignKey(User, on_delete=models.CASCADE ,related_name='commandes_principales')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente')
    adresse = models.CharField(max_length=255, blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    paye = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0.00)

    def __str__(self):
        return f"Commande: {self.id} - {self.client.username}"
    

    class LigneCommande(models.Model):
 #représente un produit et sa quantité dans un panier/commande
        commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignescommande')
        produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name="lignescommande")
        quantite = models.PositiveIntegerField(default=1)
        prix_unitaire = models.DecimalField(max_digits=10,decimal_places=0)



    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} (Commande {self.commande.id})"



