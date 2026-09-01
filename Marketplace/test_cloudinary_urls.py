#!/usr/bin/env python
"""Test que les images pointent vers Cloudinary."""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from produits.models import Produit, ProduitImage, Categorie

print("\n" + "="*70)
print("🔍 VÉRIFIER LES URLS DES IMAGES")
print("="*70 + "\n")

# Produit
p = Produit.objects.first()
if p:
    print(f"Produit: {p.nom}")
    print(f"Image: {p.image}")
    print(f"Cloudinary: {'✅' if '/samamarket/' in str(p.image) else '❌'}\n")

# Image variante
img = ProduitImage.objects.first()
if img:
    print(f"Image Variante ID: {img.id}")
    print(f"Image: {img.image}")
    print(f"Cloudinary: {'✅' if '/samamarket/' in str(img.image) else '❌'}\n")

# Catégorie
cat = Categorie.objects.first()
if cat:
    print(f"Catégorie: {cat.nom}")
    print(f"Image: {cat.image}")
    print(f"Cloudinary: {'✅' if '/samamarket/' in str(cat.image) else '❌'}\n")

print("="*70)
