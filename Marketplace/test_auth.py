#!/usr/bin/env python
"""
Test script pour vérifier l'authentification
"""
import os
import sys
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
sys.stdout.reconfigure(encoding='utf-8')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

print("=" * 60)
print("TEST D'AUTHENTIFICATION - API LOGIN")
print("=" * 60)

# Test data
test_credentials = [
    {'username': 'vendeur1', 'password': 'vendeur123'},
    {'username': 'client1', 'password': 'client123'},
    {'username': 'admin', 'password': 'admin123'},
    # Test avec email
    {'username': 'vendeur1@example.com', 'password': 'vendeur123'},
]

for creds in test_credentials:
    print(f"\n🔍 Test avec: {creds['username']}")
    print("-" * 60)
    
    # Vérifier si l'utilisateur existe
    username = creds['username']
    email = None
    
    if '@' in username:
        email = username
        try:
            user = User.objects.get(email=email)
            print(f"   ✓ Utilisateur trouvé par email: {user.username}")
        except User.DoesNotExist:
            print(f"   ✗ Utilisateur avec email '{email}' introuvable")
            continue
    else:
        try:
            user = User.objects.get(username=username)
            print(f"   ✓ Utilisateur trouvé: {user.username}")
        except User.DoesNotExist:
            print(f"   ✗ Utilisateur '{username}' introuvable")
            continue
    
    # Vérifier l'activation
    print(f"   ✓ Compte actif: {user.is_active}")
    
    # Vérifier le mot de passe
    password_match = user.check_password(creds['password'])
    print(f"   ✓ Mot de passe correct: {password_match}")
    
    if password_match:
        # Générer les tokens
        try:
            refresh = RefreshToken.for_user(user)
            print(f"   ✅ AUTHENTIFICATION RÉUSSIE!")
            print(f"      Rôle: {user.role}")
            print(f"      Access Token: {str(refresh.access_token)[:50]}...")
        except Exception as e:
            print(f"   ❌ Erreur lors de la génération du token: {e}")

print("\n" + "=" * 60)
print("✨ Test d'authentification terminé")
print("=" * 60)

# Afficher la liste des utilisateurs
print("\n📋 Utilisateurs dans la base de données:")
print("-" * 60)
for user in User.objects.all():
    print(f"  • {user.username:20} ({user.email:30}) - {user.role:10} - Actif: {user.is_active}")
