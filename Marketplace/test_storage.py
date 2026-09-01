#!/usr/bin/env python
"""Test custom storage."""

import os
import sys

# Ajouter le chemin du projet
sys.path.insert(0, r'c:\Users\PAPSALL\Documents\Premierprojet\SamaMarket\Marketplace')

# Config env
os.environ.setdefault('CLOUDINARY_CLOUD_NAME', 'n4l6q6cy')
os.environ.setdefault('CLOUDINARY_API_KEY', '717338345964995')
os.environ.setdefault('CLOUDINARY_API_SECRET', 'a4fDtqB9GgcU8iHvWqZrovJErzU')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')

import django
django.setup()

from Marketplace.storage import CustomCloudinaryMediaStorage

storage = CustomCloudinaryMediaStorage()

print("\n" + "="*70)
print("🔍 TEST CUSTOM CLOUDINARY STORAGE")
print("="*70 + "\n")

test_cases = [
    '/samamarket/demo.jpg',
    'samamarket/demo.jpg',
    'produits/demo.jpg',
    '/produits/demo.jpg',
    'https://example.com/image.jpg',
]

for test in test_cases:
    url = storage.url(test)
    print(f"Input:  {test:<40} ")
    print(f"Output: {url}")
    print()
