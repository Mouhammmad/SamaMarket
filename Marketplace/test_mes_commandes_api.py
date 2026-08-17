#!/usr/bin/env python
"""Test the mes_commandes endpoint directly"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
import django
django.setup()

import json
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from commandes.views import CommandeViewSet
from commandes.serializers import CommandeSerializer

User = get_user_model()
user = User.objects.get(email='testclient@test.com')

# Create a mock request
factory = APIRequestFactory()
request = factory.get('/api/commandes/commandes/mes_commandes/')
request.user = user

# Create viewset instance
viewset = CommandeViewSet()
viewset.request = request
viewset.format_kwarg = None

# Call the action
response = viewset.mes_commandes(request)

print("=" * 80)
print("MES COMMANDES ENDPOINT TEST")
print("=" * 80)
print(f"Status Code: {response.status_code}")
print(f"Data Type: {type(response.data)}")
print(f"Data Count: {len(response.data) if isinstance(response.data, list) else 'N/A'}")
print("")

if isinstance(response.data, list):
    print(f"Found {len(response.data)} commandes:")
    for cmd in response.data[:3]:
        print(f"\n  • {cmd.get('numero')}: {cmd.get('statut')}")
        print(f"    - Montant: {cmd.get('sous_total')} FCFA")
        print(f"    - Lignes: {len(cmd.get('lignes', []))} items")
        if cmd.get('lignes'):
            for ligne in cmd.get('lignes', [])[:2]:
                print(f"      └─ {ligne.get('produit', {}).get('nom')}: {ligne.get('quantite')}x {ligne.get('prix_unitaire')}")
else:
    print("ERROR: Response is not a list!")
    print(f"Response: {json.dumps(response.data, indent=2, default=str)}")

print("\n" + "=" * 80)
