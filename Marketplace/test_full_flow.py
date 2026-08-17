#!/usr/bin/env python
import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User
from boutiques.models import Boutique
from produits.models import Produit, Favori, Avis
from commandes.models import Commande, Panier, LigneCommande
from django.utils import timezone
from datetime import timedelta

# 1. Get test user
user = User.objects.get(email='testclient@test.com')
print(f"✓ User found: {user.email}")

# 2. Get a vendor
vendor = User.objects.filter(role='VENDOR').first()
if not vendor:
    vendor = User.objects.create_user(
        username='testvendor',
        email='testvendor@test.com',
        password='testvendor123',
        first_name='Test',
        last_name='Vendor',
        role='VENDOR'
    )
print(f"✓ Vendor found/created: {vendor.email}")

# 3. Create/get a shop
boutique = Boutique.objects.filter(responsable=vendor).first()
if not boutique:
    boutique = Boutique.objects.create(
        nom="Boutique Test",
        description="Test shop",
        responsable=vendor,
        ville="Dakar"
    )
print(f"✓ Shop found/created: {boutique.nom}")

# 4. Get or create products
produits = Produit.objects.filter(boutique=boutique)[:2]
if len(produits) < 2:
    produits = []
    for i in range(2):
        p = Produit.objects.create(
            nom=f"Product Test {i+1}",
            description=f"Test product {i+1}",
            prix=Decimal('5000.00'),
            quantite=10,
            boutique=boutique,
            categorie="Mode"
        )
        produits.append(p)

print(f"✓ Products found/created: {[p.nom for p in produits]}")

# 5. Create a favorite
if produits:
    favori, created = Favori.objects.get_or_create(
        utilisateur=user,
        produit=produits[0]
    )
    if created:
        print(f"✓ Favorite created: {produits[0].nom}")
    else:
        print(f"✓ Favorite already exists: {produits[0].nom}")

# 6. Create an order
commande = None
if produits:
    commande = Commande.objects.create(
        utilisateur=user,
        statut='en_attente',
        adresse_livraison="Dakar, Plateau",
        notes="Commande de test",
        boutique=boutique
    )
    print(f"✓ Order created: {commande.numero}")
    
    # Add order lines
    for produit in produits:
        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=1,
            prix_unitaire=produit.prix
        )
    print(f"✓ Order lines created: {commande.lignes.count()}")

# 7. Create a review
if produits:
    avis, created = Avis.objects.get_or_create(
        utilisateur=user,
        produit=produits[0],
        defaults={
            'note': 5,
            'commentaire': 'Excellent produit, très satisfait!',
            'date_creation': timezone.now()
        }
    )
    if created:
        print(f"✓ Review created: {avis.note} stars")
    else:
        print(f"✓ Review already exists: {avis.note} stars")

# 8. Update order status to trigger notification
if commande:
    commande.statut = 'confirme'
    commande.save()
    print(f"✓ Order status updated to: {commande.statut}")

# 9. Check notifications
from commandes.models import Notification
notifications = Notification.objects.filter(utilisateur=user)
print(f"\n✓ Notifications for user: {notifications.count()}")
for notif in notifications[:5]:
    print(f"  - {notif.message} (Lue: {notif.lue})")

# 10. Check resume endpoint data
print(f"\n✓ User data summary:")
print(f"  - Orders: {Commande.objects.filter(utilisateur=user).count()}")
print(f"  - Favorites: {Favori.objects.filter(utilisateur=user).count()}")
print(f"  - Reviews: {Avis.objects.filter(utilisateur=user).count()}")
print(f"  - Notifications: {notifications.count()}")
print(f"  - Notification preferences:")
print(f"    * Commandes: {user.notif_commandes}")
print(f"    * Promos: {user.notif_promos}")
print(f"    * Favoris: {user.notif_favoris}")
print(f"    * Newsletter: {user.notif_newsletter}")

print("\n✅ Test completed successfully!")
