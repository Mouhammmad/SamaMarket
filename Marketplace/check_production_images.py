#!/usr/bin/env python
"""Vérifier les images en production sur Render."""

import requests
import json

print("\n" + "="*70)
print("🔍 VÉRIFIER LES IMAGES EN PRODUCTION")
print("="*70 + "\n")

try:
    # Récupérer un produit depuis l'API en production
    response = requests.get("https://samamarket.onrender.com/api/produits/?limit=1")
    data = response.json()
    
    if data.get('results'):
        produit = data['results'][0]
        print(f"Produit: {produit.get('nom', 'N/A')}")
        print(f"Image: {produit.get('image', 'VIDE')}")
        print(f"URL complète: https://res.cloudinary.com/n4l6q6cy/image/upload/v1/{produit.get('image', '')}")
    else:
        print("❌ Pas de produit trouvé")
    
    print("\n" + "="*70)
    print("📋 Toutes les URLs (premiers 5 produits)")
    print("="*70 + "\n")
    
    response = requests.get("https://samamarket.onrender.com/api/produits/?limit=5")
    data = response.json()
    
    for i, produit in enumerate(data.get('results', []), 1):
        image = produit.get('image', '')
        status = "✅" if image and '/samamarket/' in image else "❌" if image else "❌ VIDE"
        print(f"{i}. {produit.get('nom', 'N/A'):<40} {status:5} {image}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
