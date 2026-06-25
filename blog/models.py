from django.db import models
from django.contrib.auth.models import User
#utilisation d'un signal django
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.
class Post(models.Model):
    titre =models.CharField(max_length=200)
    contenu = models.TextField()

def __str__(self):
    return self.nom

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
    prix = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    disponible =  models.BooleanField(default=True, verbose_name="Disponible/Actif")
    
    #pour deactiver automatiquement le produit quand le stock est null
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.disponible = False
        else:
            self.disponible = True #reactive le produit si le stock est ajouté
        super().save(*args, **kwargs)

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
    client= models.ForeignKey(User, on_delete=models.CASCADE ,related_name='commandes')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente' )
    adresse = models.CharField(max_length=255)
    cree_le = models.DateTimeField(auto_now_add=True)
    paye = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"Commande {self.id} - {self.client.username} "
    
class LigneCommande(models.Model):
#représente un produit et sa quantité dans un panier/commande
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.quantite} * {self.produit.nom}"
    
    def obtenir_cout_total(self):
        return self.prix_unitaire * self.quantite
    

#Ce code s'execute automatiquement avant chaque enregistrement en base de données
@receiver(pre_save,sender=Produit)
def verifier_stock_disponible(sender, instance, **kwargs):
    if instance.stock == 0:
        instance.disponible = False
    else:
        instance.disponible = True # recoche la case si vous remettez du stock
