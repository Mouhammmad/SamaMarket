#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Définir les utilisateurs de test avec des mots de passe simples
test_users = [
    {
        'username': 'vendeur1',
        'password': 'vendeur123',
        'email': 'vendeur1@example.com',
        'first_name': 'Vendeur',
        'last_name': 'Test',
        'role': 'VENDOR'
    },
    {
        'username': 'client1',
        'password': 'client123',
        'email': 'client1@example.com',
        'first_name': 'Client',
        'last_name': 'Demo',
        'role': 'CUSTOMER'
    },
    {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@sama.local',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'ADMIN'
    }
]

for user_data in test_users:
    username = user_data['username']
    password = user_data['password']
    
    try:
        user = User.objects.get(username=username)
        # Réinitialiser le mot de passe
        user.set_password(password)
        user.is_active = True
        user.save()
        print(f"✅ Utilisateur '{username}' - Mot de passe réinitialisé")
        print(f"   Username: {username}, Password: {password}")
    except User.DoesNotExist:
        print(f"❌ Utilisateur '{username}' non trouvé")

print("\n✨ Configuration des utilisateurs de test terminée!")
print("\nUtilisateurs disponibles pour tester:")
print("-" * 50)
for user in test_users:
    print(f"  • {user['username']}: {user['password']}")
print("-" * 50)
