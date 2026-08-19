#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User
from boutiques.models import Boutique
from rest_framework_simplejwt.tokens import RefreshToken
import json

# Get first vendor user
vendors = User.objects.filter(role='VENDOR')
print(f"Total vendors: {vendors.count()}")

for vendor in vendors[:3]:  # Test first 3 vendors
    print(f"\n--- Vendor: {vendor.username} ---")
    try:
        boutique = Boutique.objects.get(responsable=vendor)
        print(f"✓ Has boutique: {boutique.nom}")
        print(f"  Email: {boutique.email}")
        print(f"  Phone: {boutique.telephone}")
        print(f"  Delivery zones: {boutique.zones_livraison}")
        print(f"  Shipping fees: {boutique.frais_livraison}")
        print(f"  Wave active: {boutique.wave_actif}")
        
        # Generate token for testing
        refresh = RefreshToken.for_user(vendor)
        access_token = str(refresh.access_token)
        print(f"  Token (first 50 chars): {access_token[:50]}...")
        
    except Boutique.DoesNotExist:
        print(f"✗ No boutique for {vendor.username}")
