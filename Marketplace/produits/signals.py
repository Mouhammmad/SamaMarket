"""
Signal handlers for automatic Cloudinary image uploads.
Ensures all new images are uploaded to Cloudinary.
"""

import os
import cloudinary
import cloudinary.uploader
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from pathlib import Path


def upload_to_cloudinary(image_field):
    """Upload an image field to Cloudinary."""
    
    if not image_field or not image_field.name:
        return None
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    if not cloud_name:
        return None
    
    try:
        image_path = image_field.path
        
        if not os.path.exists(image_path):
            return None
        
        # Upload to Cloudinary with cloud-based public_id
        filename = Path(image_path).name
        public_id = f"samamarket/{filename}"
        
        result = cloudinary.uploader.upload(
            image_path,
            public_id=public_id,
            overwrite=True,
            resource_type='auto'
        )
        
        return f"/samamarket/{filename}"
    
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None


# Produits
@receiver(post_save, sender='produits.Produit')
def produit_image_to_cloudinary(sender, instance, created, **kwargs):
    """Upload product image to Cloudinary after save."""
    
    if instance.image and instance.image.name:
        # If not already a Cloudinary path, upload it
        if '/samamarket/' not in str(instance.image):
            cloudinary_path = upload_to_cloudinary(instance.image)
            if cloudinary_path:
                instance.image = cloudinary_path
                # Save without triggering signal again
                sender.objects.filter(pk=instance.pk).update(image=instance.image)


# Produit Images (variantes)
@receiver(post_save, sender='produits.ProduitImage')
def produit_image_variant_to_cloudinary(sender, instance, created, **kwargs):
    """Upload variant image to Cloudinary after save."""
    
    if instance.image and instance.image.name:
        # If not already a Cloudinary path, upload it
        if '/samamarket/' not in str(instance.image):
            cloudinary_path = upload_to_cloudinary(instance.image)
            if cloudinary_path:
                instance.image = cloudinary_path
                # Save without triggering signal again
                sender.objects.filter(pk=instance.pk).update(image=instance.image)


# Categories
@receiver(post_save, sender='produits.Categorie')
def categorie_image_to_cloudinary(sender, instance, created, **kwargs):
    """Upload category image to Cloudinary after save."""
    
    if instance.image and instance.image.name:
        # If not already a Cloudinary path, upload it
        if '/samamarket/' not in str(instance.image):
            cloudinary_path = upload_to_cloudinary(instance.image)
            if cloudinary_path:
                instance.image = cloudinary_path
                # Save without triggering signal again
                sender.objects.filter(pk=instance.pk).update(image=instance.image)


# Boutiques
@receiver(post_save, sender='boutiques.Boutique')
def boutique_image_to_cloudinary(sender, instance, created, **kwargs):
    """Upload shop image to Cloudinary after save."""
    
    images_to_check = [instance.logo, instance.banniere]
    
    for image_field in images_to_check:
        if image_field and image_field.name:
            if '/samamarket/' not in str(image_field):
                cloudinary_path = upload_to_cloudinary(image_field)
                if cloudinary_path:
                    if image_field == instance.logo:
                        instance.logo = cloudinary_path
                    elif image_field == instance.banniere:
                        instance.banniere = cloudinary_path
    
    # Save all changes
    sender.objects.filter(pk=instance.pk).update(
        logo=instance.logo,
        banniere=instance.banniere
    )
