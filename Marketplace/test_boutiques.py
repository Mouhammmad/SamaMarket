#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User
from boutiques.models import Boutique

vendors = User.objects.filter(role='VENDOR')
print(f"Total VENDOR: {vendors.count()}")

for v in vendors[:5]:
    try:
        boutique = Boutique.objects.get(responsable=v)
        print(f"✓ {v.username} a boutique: {boutique.nom}")
    except Boutique.DoesNotExist:
        print(f"✗ {v.username} N'A PAS de boutique")
