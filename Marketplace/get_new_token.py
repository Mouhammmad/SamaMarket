#!/usr/bin/env python
"""Get a fresh JWT token for the test user"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
import django
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

# Get or create test user
user, created = User.objects.get_or_create(
    email='testclient@test.com',
    defaults={
        'username': 'testclient',
        'first_name': 'Test',
        'last_name': 'Client',
        'role': 'client',
        'is_active': True,
        'is_verified': True
    }
)

# If user exists but password not set, set it
if not user.check_password('password123'):
    user.set_password('password123')
    user.save()

# Generate tokens
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)

print("=" * 80)
print("NEW JWT TOKEN")
print("=" * 80)
print(f"User: {user.email}")
print(f"Access Token: {access_token}")
print("=" * 80)
print("\nUse this in browser console:")
print(f"localStorage.setItem('access_token', '{access_token}');")
print(f"localStorage.setItem('refresh_token', '{str(refresh)}');")
print("=" * 80)
