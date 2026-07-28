import os
import shutil
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from django.conf import settings
from produits.models import Produit
from boutiques.models import Boutique

# Paths
FRONT_ASSETS = os.path.abspath(r"c:\Users\PAPSALL\Documents\Premierprojet\SamaMaket-Front\Marketplace\src\assets\images")
MEDIA_ROOT = settings.MEDIA_ROOT

print('Front assets dir:', FRONT_ASSETS)
print('Media root:', MEDIA_ROOT)

os.makedirs(os.path.join(MEDIA_ROOT, 'produits'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'boutiques'), exist_ok=True)

# Mapping source files to model instances (by name)
product_map = {
    'Echarpe Bazin': 'product.png',
    'Robe Wax': 'product.png',
    'Bracelet': 'product.png',
}

boutique_map = {
    'Couture Moderne Dakar': 'shop.png',
}

# Copy product images and attach
for prod_name, filename in product_map.items():
    src = os.path.join(FRONT_ASSETS, filename)
    if not os.path.exists(src):
        print(f'Source not found for {prod_name}: {src}')
        continue
    dst_name = f"{prod_name.replace(' ', '_')}.png"
    dst = os.path.join(MEDIA_ROOT, 'produits', dst_name)
    shutil.copyfile(src, dst)
    try:
        p = Produit.objects.filter(nom=prod_name).first()
        if p:
            p.image.name = os.path.join('produits', dst_name).replace('\\', '/')
            p.save()
            print(f'Attached image to product {prod_name}: {p.image.url}')
        else:
            print(f'Product not found: {prod_name}')
    except Exception as e:
        print('Error attaching product image', prod_name, e)

# Copy boutique logos and attach
for boutique_name, filename in boutique_map.items():
    src = os.path.join(FRONT_ASSETS, filename)
    if not os.path.exists(src):
        print(f'Source not found for boutique {boutique_name}: {src}')
        continue
    dst_name = f"{boutique_name.replace(' ', '_')}.png"
    dst = os.path.join(MEDIA_ROOT, 'boutiques', dst_name)
    shutil.copyfile(src, dst)
    try:
        b = Boutique.objects.filter(nom=boutique_name).first()
        if b:
            b.logo.name = os.path.join('boutiques', dst_name).replace('\\', '/')
            b.save()
            print(f'Attached logo to boutique {boutique_name}: {b.logo.url}')
        else:
            print(f'Boutique not found: {boutique_name}')
    except Exception as e:
        print('Error attaching boutique logo', boutique_name, e)

print('Done')
