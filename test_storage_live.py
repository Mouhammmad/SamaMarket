#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from produits.models import Produit
from django.core.files.storage import default_storage
from django.test import Client
import json

print('=' * 60)
print('TEST STORAGE BACKEND')
print('=' * 60)

# Test 1: Vérifier le storage backend
print(f'\n1. Storage Backend Class: {type(default_storage).__name__}')
print(f'   Module: {type(default_storage).__module__}')

# Test 2: Vérifier une image réelle
print(f'\n2. Testing Image URLs:')
produits = Produit.objects.filter(image__isnull=False)[:3]
if produits:
    for p in produits:
        print(f'\n   Product ID: {p.id}')
        print(f'   Raw image field: {p.image}')
        try:
            url = p.image.url
            print(f'   Computed URL: {url}')
            if 'cloudinary' in url:
                print(f'   ✅ OK - URL is from Cloudinary')
            else:
                print(f'   ❌ PROBLEM - URL is NOT from Cloudinary')
        except Exception as e:
            print(f'   ❌ Error getting URL: {e}')
else:
    print('   ⚠️  No products with images found')

# Test 3: Test API response
print(f'\n3. Testing API Response:')
try:
    client = Client()
    response = client.get('/api/produits/?limit=1')
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            prod = data['results'][0]
            print(f'   Product: {prod.get("nom")}')
            print(f'   API image: {prod.get("image")}')
            if prod.get('image') and 'cloudinary' in prod.get('image', ''):
                print(f'   ✅ OK - API returns Cloudinary URL')
            else:
                print(f'   ❌ PROBLEM - API does NOT return Cloudinary URL')
        else:
            print('   ⚠️  No products in API response')
    else:
        print(f'   ❌ API Error: {response.status_code}')
except Exception as e:
    print(f'   ❌ Error testing API: {e}')

print('\n' + '=' * 60)
