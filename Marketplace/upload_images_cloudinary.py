#!/usr/bin/env python
"""
Upload les images existantes vers Cloudinary.
À exécuter APRÈS avoir configuré Cloudinary sur Render.
"""

import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.conf import settings
from produits.models import Produit, ProduitImage, Categorie
import cloudinary
import cloudinary.uploader
from django.core.files.base import ContentFile
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def upload_to_cloudinary():
    """Upload les images vers Cloudinary."""
    
    print("\n" + "="*70)
    print("📤 UPLOADER LES IMAGES VERS CLOUDINARY")
    print("="*70)
    
    # Vérifier Cloudinary
    try:
        import cloudinary.uploader
        
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if not (cloud_name and api_key and api_secret):
            print("\n❌ Variables Cloudinary manquantes!")
            print(f"   CLOUD_NAME: {cloud_name}")
            print(f"   API_KEY: {api_key}")
            print(f"   API_SECRET: {api_secret}")
            return False
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        print(f"\n✅ Cloudinary configuré: {cloud_name}")
    except Exception as e:
        print(f"\n❌ Erreur Cloudinary: {e}")
        return False
    
    # Uploader les images des produits
    print("\n" + "="*70)
    print("📌 Produits")
    print("="*70)
    
    produits = Produit.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = produits.count()
    uploaded = 0
    errors = 0
    
    print(f"\nTotal à uploader: {total}\n")
    
    for idx, produit in enumerate(produits, 1):
        try:
            if not produit.image or not produit.image.name:
                continue
            
            # Chemin du fichier local
            image_path = produit.image.path if hasattr(produit.image, 'path') else None
            
            if image_path and os.path.exists(image_path):
                # Uploader vers Cloudinary
                public_id = f"produits/{produit.id}_{produit.image.name.split('/')[-1]}"
                result = cloudinary.uploader.upload(
                    image_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                # Mettre à jour le champ image avec l'URL Cloudinary
                produit.image.name = f"produits/{result['public_id']}.{result['format']}"
                produit.save(update_fields=['image'])
                
                print(f"  [{idx:3d}/{total}] ✅ {produit.nom[:40]:<40} → {result['secure_url'][:60]}")
                uploaded += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  {produit.nom[:40]:<40} - Fichier local non trouvé")
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ {produit.nom[:40]:<40} - ERROR: {str(e)[:50]}")
            errors += 1
    
    print(f"\n✅ Résumé Produits:")
    print(f"   - Uploadés: {uploaded}")
    print(f"   - Erreurs: {errors}")
    
    # Uploader les images des variantes
    print("\n" + "="*70)
    print("📌 Images de Variantes")
    print("="*70)
    
    images = ProduitImage.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = images.count()
    uploaded = 0
    errors = 0
    
    print(f"\nTotal à uploader: {total}\n")
    
    for idx, img in enumerate(images, 1):
        try:
            if not img.image or not img.image.name:
                continue
            
            # Chemin du fichier local
            image_path = img.image.path if hasattr(img.image, 'path') else None
            
            if image_path and os.path.exists(image_path):
                # Uploader vers Cloudinary
                public_id = f"produits/images/{img.id}_{img.image.name.split('/')[-1]}"
                result = cloudinary.uploader.upload(
                    image_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                # Mettre à jour
                img.image.name = f"produits/images/{result['public_id']}.{result['format']}"
                img.save(update_fields=['image'])
                
                print(f"  [{idx:3d}/{total}] ✅ Image {img.id} → {result['secure_url'][:60]}")
                uploaded += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  Image {img.id} - Fichier local non trouvé")
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ Image {img.id} - ERROR: {str(e)[:50]}")
            errors += 1
    
    print(f"\n✅ Résumé Images:")
    print(f"   - Uploadés: {uploaded}")
    print(f"   - Erreurs: {errors}")
    
    # Uploader les images des catégories
    print("\n" + "="*70)
    print("📌 Catégories")
    print("="*70)
    
    categories = Categorie.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = categories.count()
    uploaded = 0
    errors = 0
    
    print(f"\nTotal à uploader: {total}\n")
    
    for idx, cat in enumerate(categories, 1):
        try:
            if not cat.image or not cat.image.name:
                continue
            
            # Chemin du fichier local
            image_path = cat.image.path if hasattr(cat.image, 'path') else None
            
            if image_path and os.path.exists(image_path):
                # Uploader vers Cloudinary
                public_id = f"categories/{cat.id}_{cat.image.name.split('/')[-1]}"
                result = cloudinary.uploader.upload(
                    image_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                # Mettre à jour
                cat.image.name = f"categories/{result['public_id']}.{result['format']}"
                cat.save(update_fields=['image'])
                
                print(f"  [{idx:3d}/{total}] ✅ {cat.nom[:40]:<40} → {result['secure_url'][:60]}")
                uploaded += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  {cat.nom[:40]:<40} - Fichier local non trouvé")
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ {cat.nom[:40]:<40} - ERROR: {str(e)[:50]}")
            errors += 1
    
    print(f"\n✅ Résumé Catégories:")
    print(f"   - Uploadés: {uploaded}")
    print(f"   - Erreurs: {errors}")
    
    print("\n" + "="*70)
    print("✨ UPLOAD TERMINÉ")
    print("="*70)
    print("\nℹ️  Les images sont maintenant dans Cloudinary!")
    print("    Les URLs dans la BD ont été mises à jour automatiquement.")
    print("    En production, Cloudinary servira les images directement.\n")
    
    return True

if __name__ == '__main__':
    success = upload_to_cloudinary()
    exit(0 if success else 1)
