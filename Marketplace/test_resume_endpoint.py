#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from comptes.models import User
import json

# Get test user and generate JWT token
user = User.objects.get(email='testclient@test.com')
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print(f"✓ User: {user.email}")
print(f"✓ Access Token: {access_token[:50]}...")

# Test the resume endpoint
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
response = client.get('/api/commandes/commandes/resume/')

print(f"\n✓ Resume endpoint status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"\nResume Data:")
    print(f"  - Commandes: {len(data.get('commandes', []))}")
    print(f"  - Favoris: {len(data.get('favoris', []))}")
    print(f"  - Avis: {len(data.get('avis', []))}")
    print(f"  - Notifications: {len(data.get('notifications', []))}")
    print(f"  - Promotions: {len(data.get('promotions_favoris', []))}")
    
    # Display details
    if data.get('commandes'):
        print(f"\nCommandes:")
        for cmd in data['commandes']:
            print(f"  - {cmd.get('numero')}: {cmd.get('statut')} ({cmd.get('montant_total')} FCFA)")
    
    if data.get('favoris'):
        print(f"\nFavoris:")
        for fav in data['favoris']:
            print(f"  - {fav.get('produit', {}).get('nom')}")
    
    if data.get('avis'):
        print(f"\nAvis:")
        for avis in data['avis']:
            print(f"  - {avis.get('produit', {}).get('nom')}: {avis.get('note')} stars - {avis.get('commentaire')[:50]}")
else:
    print(f"Error: {response.text}")

print("\n✅ Test completed!")
