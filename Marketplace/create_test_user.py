#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User

# Créer un utilisateur de test
user = User.objects.create_user(
    username='testclient',
    email='testclient@test.com',
    password='testpassword123',
    first_name='Test',
    last_name='Client',
    role='CUSTOMER'
)

print(f"Utilisateur créé: {user.email}")
print(f"Préférences de notification - Commandes: {user.notif_commandes}, Promos: {user.notif_promos}, Favoris: {user.notif_favoris}, Newsletter: {user.notif_newsletter}")
