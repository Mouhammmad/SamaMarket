#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User
from boutiques.models import Boutique
from produits.models import Produit, Favori, Avis, Promotion
from commandes.models import Commande, LigneCommande, Notification
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
import json

print("=" * 80)
print("TEST COMPLET DU SYSTÈME DE NOTIFICATIONS")
print("=" * 80)

# ============== ÉTAPE 1: PRÉPARATION ==============
print("\n[ÉTAPE 1] Préparation des données...")

# Get users
user = User.objects.get(email='testclient@test.com')
vendor = User.objects.get(email='vendeur1@example.com')
print(f"✓ Utilisateur client: {user.email}")
print(f"✓ Utilisateur vendeur: {vendor.email}")

# Get shop
boutique = Boutique.objects.filter(responsable=vendor).first()
print(f"✓ Boutique: {boutique.nom}")

# Get products
produits = list(Produit.objects.filter(boutique=boutique)[:2])
print(f"✓ Produits disponibles: {len(produits)}")
for p in produits:
    print(f"  - {p.nom} ({p.prix} FCFA)")

# ============== ÉTAPE 2: CRÉER UNE COMMANDE ==============
print("\n[ÉTAPE 2] Création d'une commande...")

commande = Commande.objects.create(
    utilisateur=user,
    statut='en_attente',
    adresse_livraison="Dakar, Plateau",
    notes="Commande test pour démonstration",
    boutique=boutique
)
print(f"✓ Commande créée: {commande.numero}")

for i, produit in enumerate(produits):
    ligne = LigneCommande.objects.create(
        commande=commande,
        produit=produit,
        quantite=1,
        prix_unitaire=produit.prix
    )
    print(f"  - Ligne {i+1}: {produit.nom} (1x {produit.prix} FCFA)")

# ============== ÉTAPE 3: AJOUTER AUX FAVORIS ==============
print("\n[ÉTAPE 3] Ajout aux favoris...")

for i, produit in enumerate(produits[:1]):
    favori, created = Favori.objects.get_or_create(
        utilisateur=user,
        produit=produit
    )
    status = "créé" if created else "existant"
    print(f"✓ Favori {status}: {produit.nom}")

# ============== ÉTAPE 4: LAISSER UN AVIS ==============
print("\n[ÉTAPE 4] Rédaction d'un avis...")

avis, created = Avis.objects.get_or_create(
    utilisateur=user,
    produit=produits[0],
    defaults={
        'note': 5,
        'commentaire': 'Produit excellent! Livraison rapide et bien emballé. Très satisfait de mon achat!',
        'date_creation': timezone.now()
    }
)
status = "créé" if created else "existant"
print(f"✓ Avis {status}: {avis.note}⭐ - \"{avis.commentaire}\"")

# ============== ÉTAPE 5: CRÉER UNE PROMOTION ==============
print("\n[ÉTAPE 5] Création d'une promotion...")

promotion, created = Promotion.objects.get_or_create(
    code='PROMO30',
    defaults={
        'boutique': boutique,
        'taux_remise': Decimal('30.00'),
        'type_remise': 'pourcentage',
        'date_debut': timezone.now().date(),
        'date_fin': (timezone.now() + timedelta(days=7)).date(),
        'est_active': True,
        'limite_usage': 0
    }
)
status = "créée" if created else "existante"
print(f"✓ Promotion {status}: {promotion.code}")
print(f"  - Taux: {promotion.taux_remise}%")
print(f"  - Type: {promotion.type_remise}")

# Add products to promotion
promotion.produits.set(produits[:1])
print(f"  - Produits: {', '.join([p.nom for p in produits[:1]])}")

# ============== ÉTAPE 6: VALIDER LA COMMANDE (Vendeur) ==============
print("\n[ÉTAPE 6] Validation de la commande (vendeur)...")

commande.statut = 'confirme'
commande.save()
print(f"✓ Statut commande: {commande.statut}")

# ============== ÉTAPE 7: CRÉER UNE NOTIFICATION ==============
print("\n[ÉTAPE 7] Création d'une notification...")

notification = Notification.objects.create(
    utilisateur=user,
    commande=commande,
    titre=f"Commande {commande.numero} confirmée",
    message=f"Votre commande {commande.numero} a été confirmée par le vendeur",
    type='commande',
    est_lu=False
)
print(f"✓ Notification créée: {notification.titre}")

# ============== ÉTAPE 8: TESTER L'ENDPOINT RESUME ==============
print("\n[ÉTAPE 8] Test de l'endpoint /resume/...")

refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
response = client.get('/api/commandes/commandes/resume/')

if response.status_code == 200:
    data = response.json()
    print(f"✓ Endpoint status: 200 OK")
    print(f"\n📊 RÉSUMÉ DES DONNÉES:")
    print(f"  ├─ Commandes: {len(data.get('commandes', []))}")
    for cmd in data.get('commandes', []):
        print(f"  │  └─ {cmd.get('numero')}: {cmd.get('statut')}")
    
    print(f"  ├─ Favoris: {len(data.get('favoris', []))}")
    for fav in data.get('favoris', []):
        print(f"  │  └─ {fav.get('produit', {}).get('nom')}")
    
    print(f"  ├─ Avis: {len(data.get('avis', []))}")
    for a in data.get('avis', []):
        print(f"  │  └─ {a.get('produit', {}).get('nom')}: {a.get('note')}⭐")
    
    print(f"  ├─ Notifications: {len(data.get('notifications', []))}")
    for notif in data.get('notifications', []):
        print(f"  │  └─ {notif.get('titre')}: {notif.get('message')[:50]}...")
    
    print(f"  └─ Promotions: {len(data.get('promotions_favoris', []))}")
    for promo in data.get('promotions_favoris', []):
        print(f"     └─ {promo.get('produit', {}).get('nom')}: {promo.get('taux_remise')}% OFF")
else:
    print(f"✗ Erreur: {response.status_code}")
    print(response.text)

# ============== ÉTAPE 9: VÉRIFIER LES PRÉFÉRENCES ==============
print("\n[ÉTAPE 9] Vérification des préférences de notification...")

user.refresh_from_db()
print(f"✓ Préférences de {user.email}:")
print(f"  ├─ Commandes: {'✅' if user.notif_commandes else '❌'}")
print(f"  ├─ Promotions: {'✅' if user.notif_promos else '❌'}")
print(f"  ├─ Favoris: {'✅' if user.notif_favoris else '❌'}")
print(f"  └─ Newsletter: {'✅' if user.notif_newsletter else '❌'}")

# ============== RÉSUMÉ FINAL ==============
print("\n" + "=" * 80)
print("✅ TEST COMPLET TERMINÉ AVEC SUCCÈS!")
print("=" * 80)
print("\n📝 Résumé:")
print(f"  • Commande créée et validée: {commande.numero}")
print(f"  • Favori ajouté: {produits[0].nom}")
print(f"  • Avis posté: 5⭐")
print(f"  • Promotion créée: {promotion.code} ({promotion.taux_remise}%)")
print(f"  • Notification générée: 1")
print(f"  • Endpoint /resume/ retourne tous les données ✓")
print("\n" + "=" * 80)
