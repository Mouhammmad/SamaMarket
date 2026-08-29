#!/usr/bin/env python
"""
Script pour tester si les images des produits s'affichent correctement
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from produits.models import Produit, ProduitImage
from django.conf import settings

print("=" * 70)
print("TEST DES IMAGES DES PRODUITS")
print("=" * 70)

# Test 1: Vérifier les dossiers media
print("\n1️⃣  DOSSIERS MEDIA")
print("-" * 70)

media_root = Path(settings.MEDIA_ROOT)
if media_root.exists():
    print(f"✅ Dossier media existe: {media_root}")
    
    # Compter les fichiers
    image_files = list(media_root.glob('**/*'))
    image_files = [f for f in image_files if f.is_file()]
    print(f"   Fichiers trouvés: {len(image_files)}")
    
    if image_files:
        print("   Exemples:")
        for img in image_files[:5]:
            print(f"     • {img.relative_to(media_root)}")
else:
    print(f"❌ Dossier media n'existe pas: {media_root}")

# Test 2: Vérifier les produits avec images
print("\n2️⃣  PRODUITS AVEC IMAGES")
print("-" * 70)

produits = Produit.objects.filter(image__isnull=False).exclude(image='')
print(f"Produits avec image: {produits.count()}")

if produits.exists():
    for produit in produits[:3]:
        print(f"\n  Produit: {produit.nom}")
        print(f"  Image: {produit.image.name if produit.image else 'N/A'}")
        print(f"  URL: {produit.image.url if produit.image else 'N/A'}")
else:
    print("⚠️  Aucun produit avec image trouvé")

# Test 3: Vérifier les images supplémentaires
print("\n3️⃣  IMAGES SUPPLÉMENTAIRES")
print("-" * 70)

images = ProduitImage.objects.filter(image__isnull=False).exclude(image='')
print(f"Images supplémentaires: {images.count()}")

if images.exists():
    for img in images[:3]:
        print(f"\n  Image: {img.image.name}")
        print(f"  URL: {img.image.url}")
        print(f"  Produit: {img.produit.nom if img.produit else 'N/A'}")
else:
    print("ℹ️  Aucune image supplémentaire trouvée")

# Test 4: Vérifier la configuration
print("\n4️⃣  CONFIGURATION")
print("-" * 70)

print(f"DEBUG: {settings.DEBUG}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")

# Test 5: Vérifier les fichiers media sur disque
print("\n5️⃣  STRUCTURE MEDIA SUR DISQUE")
print("-" * 70)

for category in ['produits', 'categories', 'boutiques']:
    path = media_root / category
    if path.exists():
        files = list(path.glob('*'))
        print(f"✅ {category}/: {len(files)} fichiers")
        for f in files[:3]:
            print(f"   • {f.name}")
        if len(files) > 3:
            print(f"   ... et {len(files) - 3} autres")
    else:
        print(f"⚠️  {category}/: dossier vide ou inexistant")

# Test 6: Résumé
print("\n" + "=" * 70)
print("RÉSUMÉ")
print("=" * 70)

total_produits = Produit.objects.count()
produits_avec_image = Produit.objects.filter(image__isnull=False).exclude(image='').count()
images_supplementaires = ProduitImage.objects.filter(image__isnull=False).exclude(image='').count()

print(f"\n📊 Statistiques:")
print(f"  • Total produits: {total_produits}")
print(f"  • Produits avec image: {produits_avec_image}")
print(f"  • Images supplémentaires: {images_supplementaires}")

if settings.DEBUG:
    print(f"\n✅ Mode DÉVELOPPEMENT")
    print(f"   Les images sont servies par Django")
    print(f"   URL type: {settings.MEDIA_URL}produits/image.jpg")
else:
    print(f"\n✅ Mode PRODUCTION")
    print(f"   Les images doivent être servies par WhiteNoise")
    print(f"   URL type: {settings.MEDIA_URL}produits/image.jpg")

if produits_avec_image > 0:
    print(f"\n✅ Des images sont présentes dans la base de données")
    print(f"   Vérifier qu'elles s'affichent:")
    print(f"   - Localement: http://localhost:8000/api/produits/")
    print(f"   - Production: https://samamarket.onrender.com/api/produits/")
else:
    print(f"\n⚠️  Aucune image trouvée!")
    print(f"   Uploader des images via l'admin ou l'API")

print("\n" + "=" * 70)
