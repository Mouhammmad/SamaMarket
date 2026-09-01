"""
Migration: Mettre à jour les URLs des images vers Cloudinary.
Exécutée en production lors du déploiement.
"""
from django.db import migrations
from pathlib import Path

def update_images_to_cloudinary(apps, schema_editor):
    """Migrer les chemins des images locales vers Cloudinary."""
    
    Produit = apps.get_model('produits', 'Produit')
    ProduitImage = apps.get_model('produits', 'ProduitImage')
    Categorie = apps.get_model('produits', 'Categorie')
    
    # Produits
    for produit in Produit.objects.exclude(image__exact='').exclude(image__isnull=True):
        if produit.image and produit.image.name:
            old_path = produit.image.name
            # Convertir "produits/demo.jpg" → "/samamarket/demo.jpg"
            filename = Path(old_path).name
            produit.image = f"/samamarket/{filename}"
            produit.save(update_fields=['image'])
    
    # Images de variantes
    for img in ProduitImage.objects.exclude(image__exact='').exclude(image__isnull=True):
        if img.image and img.image.name:
            old_path = img.image.name
            filename = Path(old_path).name
            img.image = f"/samamarket/{filename}"
            img.save(update_fields=['image'])
    
    # Catégories
    for cat in Categorie.objects.exclude(image__exact='').exclude(image__isnull=True):
        if cat.image and cat.image.name:
            old_path = cat.image.name
            filename = Path(old_path).name
            cat.image = f"/samamarket/{filename}"
            cat.save(update_fields=['image'])

def reverse_migration(apps, schema_editor):
    """Restaurer les chemins locaux (non recommandé)."""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('produits', '0007_promotion_date_creation'),
    ]

    operations = [
        migrations.RunPython(update_images_to_cloudinary, reverse_migration),
    ]
