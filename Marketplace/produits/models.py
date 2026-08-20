from django.db import models
from django.conf import settings

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_categories'
    )

    class Meta:
        db_table = 'produits_category'

    def __str__(self):
        return self.nom


class Produit(models.Model):
    ETAT_CHOICES = [
        ('neuf', 'Neuf'),
        ('occasion', 'Occasion'),
    ]

    boutique = models.ForeignKey(
        'boutiques.Boutique',
        on_delete=models.CASCADE,
        related_name='produits'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name='produits'
    )
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    marque = models.CharField(max_length=100, blank=True)
    sku = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    unique=True
)
    slug = models.SlugField(
    blank=True,
    null=True,
    unique=True
)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='neuf')
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.PositiveIntegerField(default=0)
    poids = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    largeur = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    hauteur = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    longueur = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    mots_cles = models.CharField(max_length=300, blank=True)
    nombre_vues = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class Favori(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoris'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='favoris'
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['utilisateur', 'produit']

    def __str__(self):
        return f"{self.utilisateur.username} → {self.produit.nom}"


class Avis(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avis'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='avis'
    )
    note = models.PositiveIntegerField()
    commentaire = models.TextField(blank=True)
    est_approuve = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['utilisateur', 'produit']

    def __str__(self):
        return f"Avis de {self.utilisateur.username} sur {self.produit.nom}"


class Promotion(models.Model):
    TYPE_CHOICES = [
        ('pourcentage', 'Pourcentage'),
        ('montant_fixe', 'Montant fixe'),
    ]
    boutique = models.ForeignKey(
        'boutiques.Boutique',
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    produits = models.ManyToManyField(
        Produit,
        related_name='promotions',
        blank=True
    )
    code = models.CharField(max_length=50, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    taux_remise = models.DecimalField(max_digits=10, decimal_places=2)
    type_remise = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=True)
    limite_usage = models.PositiveIntegerField(default=0)
    nombre_utilise = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} - {self.taux_remise}"

    def est_valide(self):
        from django.utils import timezone
        aujourd_hui = timezone.now().date()
        return (
            self.est_active and
            self.date_debut <= aujourd_hui <= self.date_fin and
            (self.limite_usage == 0 or self.nombre_utilise < self.limite_usage)
        )

class ProduitImage(models.Model):
    produit = models.ForeignKey(
        Produit,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to="produits/"
    )

    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.produit.nom} - {self.id}"

class ProduitVariante(models.Model):
    produit = models.ForeignKey(
        Produit,
        related_name="variantes",
        on_delete=models.CASCADE
    )

    nom = models.CharField(max_length=100)
    valeur = models.CharField(max_length=100)

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantite_stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="variantes/",
        blank=True,
        null=True
    )

    sku = models.CharField(
        max_length=80,
        blank=True
    )

    est_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.produit.nom} - {self.nom}: {self.valeur}"