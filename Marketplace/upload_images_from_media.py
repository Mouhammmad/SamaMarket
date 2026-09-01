#!/usr/bin/env python
"""
Télécharge les images depuis l'API locale et les upload vers Cloudinary.
À exécuter après avoir configuré Cloudinary.
"""

import os
import django
import requests
from io import BytesIO

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.conf import settings
from produits.models import Produit, ProduitImage, Categorie
import cloudinary
import cloudinary.uploader
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

def download_and_upload_to_cloudinary():
    """Télécharge les images depuis URL et les upload vers Cloudinary."""
    
    print("\n" + "="*70)
    print("📤 TÉLÉCHARGER ET UPLOADER LES IMAGES VERS CLOUDINARY")
    print("="*70)
    
    # Vérifier Cloudinary
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if not (cloud_name and api_key and api_secret):
            print("\n❌ Variables Cloudinary manquantes!")
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
    
    # Produits
    print("\n" + "="*70)
    print("📌 Produits")
    print("="*70)
    
    produits = Produit.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = produits.count()
    uploaded = 0
    errors = 0
    
    print(f"\nTotal à traiter: {total}\n")
    
    for idx, produit in enumerate(produits, 1):
        try:
            if not produit.image or not produit.image.name:
                continue
            
            # Construire l'URL de l'image locale
            image_filename = produit.image.name.split('/')[-1]
            media_path = os.path.join(settings.MEDIA_ROOT, produit.image.name)
            
            # Essayer d'uploader directement si le fichier existe
            if os.path.exists(media_path):
                print(f"  [{idx:3d}/{total}] 📂 {produit.nom[:40]:<40} (fichier local)")
                public_id = f"produits/{produit.id}_{image_filename}"
                result = cloudinary.uploader.upload(
                    media_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                # Mettre à jour avec URL Cloudinary
                produit.image = f"{public_id}.{result['format']}"
                produit.save(update_fields=['image'])
                
                print(f"       ✅ Uploadé vers: {result['public_id']}")
                uploaded += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  {produit.nom[:40]:<40} (fichier manquant)")
                # Essayer de construire une URL théorique
                if produit.image.name:
                    print(f"       → Path attendu: {media_path}")
        
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ {produit.nom[:40]:<40} - {str(e)[:50]}")
            errors += 1
    
    print(f"\n✅ Résumé Produits: {uploaded} uploadés, {errors} erreurs")
    
    # Images de variantes
    print("\n" + "="*70)
    print("📌 Images de Variantes")
    print("="*70)
    
    images = ProduitImage.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = images.count()
    uploaded_var = 0
    errors_var = 0
    
    print(f"\nTotal à traiter: {total}\n")
    
    for idx, img in enumerate(images, 1):
        try:
            if not img.image or not img.image.name:
                continue
            
            image_filename = img.image.name.split('/')[-1]
            media_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
            
            if os.path.exists(media_path):
                print(f"  [{idx:3d}/{total}] 📂 Image {img.id:<6} (fichier local)")
                public_id = f"produits/images/{img.id}_{image_filename}"
                result = cloudinary.uploader.upload(
                    media_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                img.image = f"{public_id}.{result['format']}"
                img.save(update_fields=['image'])
                
                print(f"       ✅ Uploadé vers: {result['public_id']}")
                uploaded_var += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  Image {img.id:<6} (fichier manquant)")
        
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ Image {img.id:<6} - {str(e)[:50]}")
            errors_var += 1
    
    print(f"\n✅ Résumé Images: {uploaded_var} uploadés, {errors_var} erreurs")
    
    # Catégories
    print("\n" + "="*70)
    print("📌 Catégories")
    print("="*70)
    
    categories = Categorie.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = categories.count()
    uploaded_cat = 0
    errors_cat = 0
    
    print(f"\nTotal à traiter: {total}\n")
    
    for idx, cat in enumerate(categories, 1):
        try:
            if not cat.image or not cat.image.name:
                continue
            
            image_filename = cat.image.name.split('/')[-1]
            media_path = os.path.join(settings.MEDIA_ROOT, cat.image.name)
            
            if os.path.exists(media_path):
                print(f"  [{idx:3d}/{total}] 📂 {cat.nom:<40} (fichier local)")
                public_id = f"categories/{cat.id}_{image_filename}"
                result = cloudinary.uploader.upload(
                    media_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )
                
                cat.image = f"{public_id}.{result['format']}"
                cat.save(update_fields=['image'])
                
                print(f"       ✅ Uploadé vers: {result['public_id']}")
                uploaded_cat += 1
            else:
                print(f"  [{idx:3d}/{total}] ⚠️  {cat.nom:<40} (fichier manquant)")
        
        except Exception as e:
            print(f"  [{idx:3d}/{total}] ❌ {cat.nom:<40} - {str(e)[:50]}")
            errors_cat += 1
    
    print(f"\n✅ Résumé Catégories: {uploaded_cat} uploadés, {errors_cat} erreurs")
    
    print("\n" + "="*70)
    print("✨ RÉSUMÉ TOTAL")
    print("="*70)
    print(f"\nProduits:   {uploaded}")
    print(f"Images:     {uploaded_var}")
    print(f"Catégories: {uploaded_cat}")
    print(f"TOTAL:      {uploaded + uploaded_var + uploaded_cat}")
    
    if (uploaded + uploaded_var + uploaded_cat) == 0:
        print("\n⚠️  AUCUNE IMAGE N'A PU ÊTRE UPLOADÉE!")
        print("   Les fichiers locaux n'existent pas sur le disque.")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifier le dossier SamaMarket/Marketplace/media/")
        print("   2. Importer les données avec import_data.py")
        print("   3. Re-uploader les images manuellement via l'admin")
        return False
    
    print("\n✅ Images uploadées vers Cloudinary!")
    print("   Elles apparaîtront en production.\n")
    
    return True

if __name__ == '__main__':
    success = download_and_upload_to_cloudinary()
    exit(0 if success else 1)
