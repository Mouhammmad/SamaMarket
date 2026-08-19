#!/usr/bin/env python
import os
import sys
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User
from boutiques.models import Boutique
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

# Get vendor token
vendor = User.objects.filter(role='VENDOR').first()
if not vendor:
    print("No vendor found")
    sys.exit(1)

refresh = RefreshToken.for_user(vendor)
access_token = str(refresh.access_token)

# Test API endpoint
api_url = 'http://127.0.0.1:8000/api/boutiques/ma/parametres/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

print(f"Testing API for vendor: {vendor.username}")
print(f"URL: {api_url}")
print(f"Token: {access_token[:30]}...")

try:
    response = requests.get(api_url, headers=headers, timeout=5)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"Response JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
