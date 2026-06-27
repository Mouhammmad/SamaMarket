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
        
class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('expedie', 'Expédié'),
        ('livre', 'Livré'),
        ('annule', 'Annulé'),
    ]
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adresse_livraison = models.TextField()
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.username}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    produit = models.ForeignKey(
        'catalogue.Produit',
        on_delete=models.PROTECT
    )
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def calculer_sous_total(self):
        return self.quantite * self.prix_unitaire


class Paiement(models.Model):
    METHODE_CHOICES = [
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complété'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ]
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='paiement'
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    id_transaction = models.CharField(max_length=255, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement #{self.id} - {self.methode} - {self.statut}"

class Livraison(models.Model):
    STATUT_CHOICES = [
        ('en_preparation', 'En préparation'),
        ('expedie', 'Expédié'),
        ('en_transit', 'En transit'),
        ('livre', 'Livré'),
        ('echoue', 'Échoué'),
    ]
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='livraison'
    )
    adresse = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_preparation')
    numero_suivi = models.CharField(max_length=100, unique=True)
    date_prevue = models.DateField(null=True, blank=True)
    date_livraison = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Livraison #{self.numero_suivi} - {self.statut}"