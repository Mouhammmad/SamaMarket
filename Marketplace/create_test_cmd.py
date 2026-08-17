#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from commandes.models import Commande, LigneCommande
from boutiques.models import Boutique
from produits.models import Produit
from comptes.models import User
from decimal import Decimal

# Récupérer la boutique du vendeur_test
boutique = Boutique.objects.get(id=5)

# Trouver un utilisateur client
user = User.objects.filter(username='testuser').first() or User.objects.first()

# Trouver un produit de cette boutique
produit = Produit.objects.filter(boutique=boutique).first()

if not produit:
    print('Pas de produit trouvé dans la boutique. Création d\'un produit de test...')
    produit = Produit.objects.create(
        nom='Produit Test',
        description='Produit de test pour commande',
        prix=Decimal('5000.00'),
        boutique=boutique,
        stock=100
    )

# Créer une commande de test
cmd = Commande.objects.create(
    utilisateur=user,
    adresse_livraison='123 Test Street',
    sous_total=Decimal('5000.00'),
    frais_livraison=Decimal('500.00'),
    reduction=Decimal('0.00'),
    statut='en_attente',
    mode_livraison='standard'
)

# Ajouter une ligne de commande pour que la commande soit visible du vendeur
ligne = LigneCommande.objects.create(
    commande=cmd,
    produit=produit,
    quantite=1,
    prix_unitaire=Decimal('5000.00')
)

print(f'Commande créée: {cmd.id}, {cmd.numero}, {cmd.statut}')
print(f'Boutique: {boutique.nom}')
print(f'Utilisateur: {user.username}')
print(f'Produit: {produit.nom}')
print(f'Ligne ajoutée: {ligne.id}')



