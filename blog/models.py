from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    titre =models.CharField(max_length=200)
    contenu = models.TextField()

def __str__(self):
    return self.titre

class Categorie(models.Model):
    nom=models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.nom
    
class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produit', null=True)
    nom = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)

    def __str__(self):
        return self.nom

class Commande(models.Model):
    STATUT_CHOICES =[
        ('En attente', 'En attente'),
        ('Payée', 'Payée'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée')
    ]
    #L'utilisateur "User" de django sert ici de client
    client= models.ForeignKey(User, on_delete=models.CASCADE ,related_name='commande')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente' )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.username} "
    
class LigneCommande(models.Model):
#représente un produit et sa quantité dans un panier/commande
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='Lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.quantite} * {self.produit.nom}"