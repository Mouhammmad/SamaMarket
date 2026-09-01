"""Custom storage backend to serve images from Cloudinary."""

import os
import cloudinary.uploader
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
        
        # If already a Cloudinary URL, return as-is
        if name_str.startswith('http'):
            return name_str
        
        # Remove leading slash if present
        clean_name = name_str.lstrip('/')
        
        # Convert "produits/demo.jpg" → "samamarket/demo.jpg"
        if clean_name.startswith('produits/'):
            clean_name = clean_name.replace('produits/', 'samamarket/', 1)
        
        # Build Cloudinary URL
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        base_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/v1"
        
        return f"{base_url}/{clean_name}"
