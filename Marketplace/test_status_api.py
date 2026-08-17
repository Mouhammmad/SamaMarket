#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from commandes.views import CommandeVendeurViewSet
from comptes.models import User
from commandes.models import Commande

factory = APIRequestFactory()

# Récupérer un utilisateur vendeur
vendor = User.objects.filter(role='VENDOR').first()
print(f'Vendor: {vendor.username if vendor else "None"}')
print(f'Vendor role: {vendor.role if vendor else "N/A"}')

if vendor:
    # Vérifier que la commande 43 existe et peut être vue par le vendeur
    try:
        cmd = Commande.objects.get(
            id=43,
            lignes__produit__boutique__responsable=vendor
        )
        print(f'Command 43 found: {cmd.numero}, statut={cmd.statut}')
    except Commande.DoesNotExist:
        print('Command 43 not found for this vendor')
        sys.exit(1)
    
    # Créer une requête PATCH
    request = factory.patch(
        '/api/vendeur/commandes/43/mettre_a_jour_statut/',
        {'statut': 'confirme'},
        format='json'
    )
    request.user = vendor
    
    # Appeler la vue
    viewset = CommandeVendeurViewSet()
    viewset.format_kwarg = None
    viewset.request = request
    try:
        response = viewset.mettre_a_jour_statut(request, pk=43)
        print(f'Response status: {response.status_code}')
        print(f'Response data: {response.data}')
        
        # Vérifier l'état de la BD
        cmd.refresh_from_db()
        print(f'Database statut after API call: {cmd.statut}')
    except Exception as e:
        import traceback
        print(f'Error: {e}')
        traceback.print_exc()
