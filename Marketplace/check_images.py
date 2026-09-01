#!/usr/bin/env python
"""
Script pour diagnostiquer les problèmes d'images en production.
Vérifie la configuration Cloudinary et teste les URLs.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.conf import settings
from produits.models import Produit
import logging

logger = logging.getLogger(__name__)

def check_cloudinary_config():
    """Vérifie si Cloudinary est bien configuré."""
    print("\n" + "="*60)
    print("🔍 CHECK CLOUDINARY CONFIGURATION")
    print("="*60)
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    cloudinary_url = os.getenv('CLOUDINARY_URL')
    
    print(f"\n✓ CLOUDINARY_CLOUD_NAME: {'✅ SET' if cloud_name else '❌ MISSING'}")
    print(f"✓ CLOUDINARY_API_KEY: {'✅ SET' if api_key else '❌ MISSING'}")
    print(f"✓ CLOUDINARY_API_SECRET: {'✅ SET' if api_secret else '❌ MISSING'}")
    print(f"✓ CLOUDINARY_URL: {'✅ SET' if cloudinary_url else '❌ MISSING'}")
    
    if not (cloud_name and api_key and api_secret):
        print("\n⚠️  CLOUDINARY NOT FULLY CONFIGURED")
        print("   Images will use local storage (not suitable for production)")
        return False
    
    print("\n✅ CLOUDINARY READY")
    return True

def check_storage_config():
    """Vérifie le stockage des fichiers."""
    print("\n" + "="*60)
    print("🔍 CHECK STORAGE CONFIGURATION")
    print("="*60)
    
    default_storage = settings.DEFAULT_FILE_STORAGE if hasattr(settings, 'DEFAULT_FILE_STORAGE') else 'Not set'
    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL
    
    print(f"\nDEFAULT_FILE_STORAGE: {default_storage}")
    print(f"MEDIA_ROOT: {media_root}")
    print(f"MEDIA_URL: {media_url}")
    print(f"DEBUG: {settings.DEBUG}")
    
    if 'cloudinary' in str(default_storage).lower():
        print("\n✅ Using Cloudinary for file storage")
    else:
        print("\n⚠️  Using local storage (check MEDIA_ROOT accessibility)")

def check_products_images():
    """Vérifie les images des produits."""
    print("\n" + "="*60)
    print("🔍 CHECK PRODUCTS IMAGES")
    print("="*60)
    
    products = Produit.objects.filter(image__isnull=False, image__exact='')[:5]
    total_products = Produit.objects.count()
    products_with_images = Produit.objects.exclude(image__exact='').exclude(image__isnull=True).count()
    
    print(f"\nTotal products: {total_products}")
    print(f"Products with images: {products_with_images}")
    
    if products_with_images == 0:
        print("⚠️  No products have images!")
        return
    
    print("\nSample image paths:")
    for prod in Produit.objects.exclude(image__exact='').exclude(image__isnull=True)[:3]:
        try:
            image_url = prod.image.url
            print(f"  - {prod.nom[:30]}: {image_url}")
        except Exception as e:
            print(f"  - {prod.nom[:30]}: ERROR - {e}")

def main():
    print("\n🚀 IMAGE DIAGNOSTICS - SamaMarket")
    print("Date: 2026-09-01")
    
    cloudinary_ok = check_cloudinary_config()
    check_storage_config()
    check_products_images()
    
    print("\n" + "="*60)
    print("📋 RECOMMENDATIONS")
    print("="*60)
    
    if not cloudinary_ok:
        print("\n⚠️  URGENT: Configure Cloudinary on Render:")
        print("   1. Get credentials from https://cloudinary.com/console/")
        print("   2. Add to Render Environment Variables:")
        print("      - CLOUDINARY_CLOUD_NAME")
        print("      - CLOUDINARY_API_KEY")
        print("      - CLOUDINARY_API_SECRET")
        print("   3. Redeploy")
    else:
        print("\n✅ Cloudinary is configured")
        print("   Re-upload images to populate Cloudinary")
    
    print("\n")

if __name__ == '__main__':
    main()
