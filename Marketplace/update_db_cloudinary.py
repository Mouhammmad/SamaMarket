#!/usr/bin/env python
"""
Mettre à jour la BD pour utiliser les URLs Cloudinary au lieu des chemins locaux.
"""

import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.conf import settings
from produits.models import Produit, ProduitImage, Categorie
import cloudinary

def update_database_to_cloudinary():
    """Met à jour la BD pour pointer vers Cloudinary."""
    
    print("\n" + "="*70)
    print("🔄 METTRE À JOUR LA BD VERS CLOUDINARY")
    print("="*70)
    
    # Config Cloudinary
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    if not cloud_name:
        print("\n❌ CLOUDINARY_CLOUD_NAME non configuré!")
        return False
    
    print(f"\n✅ Cloudinary configuré: {cloud_name}")
    
    # Dossier media
    media_root = Path(r"c:\Users\PAPSALL\Documents\Premierprojet\SamaMarket\Marketplace\media")
    
    # Map des fichiers uploadés
    uploaded_files = {}
    for file_path in media_root.rglob('*'):
        if file_path.is_file():
            filename = file_path.name
            if filename not in uploaded_files:
                uploaded_files[filename] = file_path
    
    print(f"\n📊 Fichiers mappés: {len(uploaded_files)}")
    
    # Mettre à jour Produits
    print("\n" + "="*70)
    print("📌 Mettre à jour les Produits")
    print("="*70 + "\n")
    
    produits = Produit.objects.exclude(image__exact='').exclude(image__isnull=True)
    updated_produits = 0
    
    for produit in produits:
        if not produit.image or not produit.image.name:
            continue
        
        # Extraire le nom du fichier
        old_path = produit.image.name
        filename = Path(old_path).name
        
        # Construire la nouvelle URL Cloudinary
        # Exemple: produits/demo.jpg → /samamarket/produits/demo.jpg
        new_path = f"/samamarket/{filename}"
        
        if old_path != new_path:
            produit.image = new_path
            produit.save(update_fields=['image'])
            print(f"  ✅ {produit.nom[:40]:<40} - {old_path} → {new_path}")
            updated_produits += 1
    
    print(f"\n✅ Produits mis à jour: {updated_produits}")
    
    # Mettre à jour Images
    print("\n" + "="*70)
    print("📌 Mettre à jour les Images de Variantes")
    print("="*70 + "\n")
    
    images = ProduitImage.objects.exclude(image__exact='').exclude(image__isnull=True)
    updated_images = 0
    
    for img in images:
        if not img.image or not img.image.name:
            continue
        
        old_path = img.image.name
        filename = Path(old_path).name
        new_path = f"/samamarket/{filename}"
        
        if old_path != new_path:
            img.image = new_path
            img.save(update_fields=['image'])
            print(f"  ✅ Image {img.id} - {old_path} → {new_path}")
            updated_images += 1
    
    print(f"\n✅ Images mises à jour: {updated_images}")
    
    # Mettre à jour Catégories
    print("\n" + "="*70)
    print("📌 Mettre à jour les Catégories")
    print("="*70 + "\n")
    
    categories = Categorie.objects.exclude(image__exact='').exclude(image__isnull=True)
    updated_categories = 0
    
    for cat in categories:
        if not cat.image or not cat.image.name:
            continue
        
        old_path = cat.image.name
        filename = Path(old_path).name
        new_path = f"/samamarket/{filename}"
        
        if old_path != new_path:
            cat.image = new_path
            cat.save(update_fields=['image'])
            print(f"  ✅ {cat.nom:<40} - {old_path} → {new_path}")
            updated_categories += 1
    
    print(f"\n✅ Catégories mises à jour: {updated_categories}")
    
    # Résumé
    print("\n" + "="*70)
    print("✨ RÉSUMÉ TOTAL")
    print("="*70)
    print(f"\n📦 Produits:   {updated_produits}")
    print(f"📸 Images:     {updated_images}")
    print(f"🏷️  Catégories: {updated_categories}")
    print(f"📊 TOTAL:      {updated_produits + updated_images + updated_categories}")
    
    total = updated_produits + updated_images + updated_categories
    if total > 0:
        print(f"\n✅ La BD a été mise à jour pour utiliser Cloudinary!")
        print(f"   Les images seront servies depuis: https://res.cloudinary.com/{cloud_name}/...")
        return True
    
    return False

if __name__ == '__main__':
    success = update_database_to_cloudinary()
    exit(0 if success else 1)
