#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User

user = User.objects.get(email='testclient@test.com')
print(f"Utilisateur: {user.email}")
print(f"Notifications - Commandes: {user.notif_commandes}, Promos: {user.notif_promos}, Favoris: {user.notif_favoris}, Newsletter: {user.notif_newsletter}")
