#!/usr/bin/env python
"""
Uploader TOUS les fichiers du dossier media/ vers Cloudinary.
"""

import os
import cloudinary
import cloudinary.uploader
from pathlib import Path

def upload_all_media_files():
    """Upploade tous les fichiers du dossier media vers Cloudinary."""
    
    print("\n" + "="*70)
    print("📤 UPLOADER TOUS LES FICHIERS MEDIA VERS CLOUDINARY")
    print("="*70)
    
    # Config Cloudinary
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
    
    # Dossier media
    media_root = Path(r"c:\Users\PAPSALL\Documents\Premierprojet\SamaMarket\Marketplace\media")
    
    if not media_root.exists():
        print(f"\n❌ Dossier media non trouvé: {media_root}")
        return False
    
    print(f"\n📁 Dossier media: {media_root}")
    
    # Récupérer tous les fichiers
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    files_to_upload = []
    
    for file_path in media_root.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            files_to_upload.append(file_path)
    
    total = len(files_to_upload)
    print(f"\n📊 Fichiers à uploader: {total}\n")
    
    if total == 0:
        print("❌ Aucun fichier à uploader!")
        return False
    
    uploaded = 0
    errors = 0
    
    for idx, file_path in enumerate(files_to_upload, 1):
        try:
            # Construire un public_id lisible
            relative_path = file_path.relative_to(media_root)
            public_id = str(relative_path.with_suffix('')).replace('\\', '/')
            
            # Uploader
            result = cloudinary.uploader.upload(
                str(file_path),
                public_id=f"samamarket/{public_id}",
                overwrite=True,
                resource_type='auto'
            )
            
            url = result.get('secure_url', '')
            filename = file_path.name
            print(f"  [{idx:3d}/{total}] ✅ {filename:<40} → OK")
            uploaded += 1
            
        except Exception as e:
            filename = file_path.name
            error_msg = str(e)[:60]
            print(f"  [{idx:3d}/{total}] ❌ {filename:<40} → {error_msg}")
            errors += 1
    
    print(f"\n" + "="*70)
    print(f"✨ RÉSUMÉ")
    print(f"="*70)
    print(f"\n✅ Uploadés: {uploaded}")
    print(f"❌ Erreurs: {errors}")
    print(f"📊 Total: {uploaded + errors}/{total}")
    
    if uploaded > 0:
        print(f"\n🎉 {uploaded} fichiers uploadés vers Cloudinary!")
        print(f"\n   Les URLs Cloudinary sont:")
        print(f"   https://res.cloudinary.com/{cloud_name}/image/upload/v1234567890/samamarket/...")
        return True
    
    return False

if __name__ == '__main__':
    success = upload_all_media_files()
    exit(0 if success else 1)
