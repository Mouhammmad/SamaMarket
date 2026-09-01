#!/usr/bin/env python
"""
Script d'initialisation de la base de données de production.
Exécuté automatiquement après les migrations.
"""

import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def create_superuser():
    """Crée un utilisateur superuser s'il n'existe pas."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@samamarket.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    if not admin_password or admin_password == 'admin123':
        logger.warning('⚠️  ATTENTION: Vous utilisez le mot de passe admin par défaut!')
        logger.warning('⚠️  Changez ADMIN_PASSWORD dans les variables d\'environnement Render!')
    
    if User.objects.filter(username=admin_username).exists():
        logger.info(f'✅ Admin {admin_username} existe déjà')
        return
    
    try:
        user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role='ADMIN'
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        logger.info(f'✅ Admin {admin_username} créé avec succès')
    except Exception as e:
        logger.error(f'❌ Erreur création admin: {e}')
        sys.exit(1)

def create_test_users():
    """Crée les utilisateurs de test si en développement."""
    if os.getenv('DEBUG', 'False').lower() == 'true':
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
            }
        ]
        
        for user_data in test_users:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                try:
                    User.objects.create_user(**user_data)
                    logger.info(f'✅ Utilisateur test {username} créé')
                except Exception as e:
                    logger.error(f'❌ Erreur création user test {username}: {e}')

if __name__ == '__main__':
    logger.info('🚀 Initialisation de la base de données...')
    create_superuser()
    create_test_users()
    logger.info('✅ Initialisation terminée')
