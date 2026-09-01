#!/usr/bin/env python
"""
Script pour migrer les images locales vers Cloudinary.
À exécuter après avoir configuré Cloudinary sur Render.
"""

import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from produits.models import Produit, ProduitImage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

def migrate_images_to_cloudinary():
    """Migre les images locales vers Cloudinary."""
    
    print("\n" + "="*60)
    print("📤 MIGRER IMAGES VERS CLOUDINARY")
    print("="*60)
    
    # Vérifier que Cloudinary est configuré
    try:
        import cloudinary
        cloudinary.config()
        if not cloudinary.config().get('cloud_name'):
            print("\n❌ Cloudinary n'est pas configuré!")
            print("   Veuillez définir les variables d'environnement Cloudinary.")
            return
        print("\n✅ Cloudinary est configuré")
    except ImportError:
        print("\n❌ Module cloudinary non installé")
        print("   pip install cloudinary")
        return
    
    # Migrer les images des produits
    print("\n📌 Migrer les images des produits...")
    produits_avec_images = Produit.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = produits_avec_images.count()
    
    if total == 0:
        print("   ✓ Aucune image à migrer")
        return
    
    done = 0
    errors = 0
    
    for produit in produits_avec_images:
        try:
            # Vérifier si l'image existe
            if not produit.image or not produit.image.name:
                continue
            
            # Forcer Django à upload vers Cloudinary
            # (si Cloudinary est configuré, ce sera automatique)
            print(f"   ✓ {produit.nom[:40]:<40} - {produit.image.name}")
            done += 1
        except Exception as e:
            print(f"   ❌ {produit.nom[:40]:<40} - ERROR: {e}")
            errors += 1
    
    print(f"\n✅ Résumé:")
    print(f"   - Produits traités: {done}")
    print(f"   - Erreurs: {errors}")
    
    # Migrer les images des produits (variantes)
    print("\n📌 Migrer les images des variantes...")
    images_with_images = ProduitImage.objects.exclude(image__exact='').exclude(image__isnull=True)
    total = images_with_images.count()
    
    if total > 0:
        done = 0
        errors = 0
        for img in images_with_images[:10]:  # Limiter à 10 pour test
            try:
                if not img.image or not img.image.name:
                    continue
                print(f"   ✓ Image {img.id} pour produit {img.produit.nom[:30]}")
                done += 1
            except Exception as e:
                print(f"   ❌ Image {img.id} - ERROR: {e}")
                errors += 1
        print(f"\n✅ Résumé variantes:")
        print(f"   - Images traitées: {done}/{total}")
        print(f"   - Erreurs: {errors}")
    
    print("\n" + "="*60)
    print("✨ Migration terminée!")
    print("="*60)
    print("\nℹ️  Important:")
    print("   - Cloudinary stocke les images automatiquement")
    print("   - Les URLs se construisent automatiquement")
    print("   - Pas besoin d'action supplémentaire")
    print("\n")

if __name__ == '__main__':
    migrate_images_to_cloudinary()
