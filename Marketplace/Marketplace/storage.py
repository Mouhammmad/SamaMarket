"""Cloudinary storage with compatibility for migrated image paths."""

import os

from cloudinary_storage.storage import MediaCloudinaryStorage


class CustomCloudinaryMediaStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that converts local paths to Cloudinary URLs.
    
    Handles:
    - /samamarket/filename.jpg → Cloudinary URL
    - produits/filename.jpg → Cloudinary URL
    - Direct Cloudinary URLs (returns as-is)
    """

    def url(self, name):
        """
        Convert local path to Cloudinary URL.
        
        Examples:
        - /samamarket/demo.jpg → https://res.cloudinary.com/.../samamarket/demo.jpg
        - produits/demo.jpg → https://res.cloudinary.com/.../samamarket/demo.jpg
        - https://... → returns as-is
        """
        
        if not name:
            return ''
        
        name_str = str(name)
        
        # Preserve URLs stored directly by an external image provider.
        if name_str.startswith(('http://', 'https://')):
            return name_str

        clean_name = name_str.lstrip('/')
        if clean_name.startswith('media/'):
            clean_name = clean_name[len('media/'):]

        if clean_name.startswith('samamarket/'):
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
            if cloud_name:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/v1/{clean_name}"

        return super().url(name)
