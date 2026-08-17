from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.test import APIRequestFactory, force_authenticate
from commandes.views import CommandeViewSet, CommandeVendeurViewSet
from boutiques.models import Boutique
from produits.models import Categorie, Produit
from comptes.models import User
from commandes.models import Panier, ArticlePanier, Commande, LigneCommande, Paiement, Notification

User = get_user_model()

customer, _ = User.objects.get_or_create(
    username='test_client',
    defaults={
        'email': 'client@example.com',
        'role': 'CUSTOMER',
        'first_name': 'Client',
        'last_name': 'Test',
        'password': 'testpass123'
    }
)

vendor, _ = User.objects.get_or_create(
    username='test_vendor',
    defaults={
        'email': 'vendor@example.com',
        'role': 'VENDOR',
        'first_name': 'Vendor',
        'last_name': 'Test',
        'password': 'testpass123'
    }
)

boutique, _ = Boutique.objects.get_or_create(responsable=vendor,
    defaults={
        'nom': 'Boutique de test',
        'description': 'Boutique de test',
        'ville': 'Dakar'
    }
)

categorie, _ = Categorie.objects.get_or_create(nom='Categorie test')

produit, _ = Produit.objects.get_or_create(
    sku='TEST-PROD-1',
    defaults={
        'boutique': boutique,
        'categorie': categorie,
        'nom': 'Produit test',
        'description': 'Un produit de test',
        'prix': '1000.00',
        'quantite_stock': 10,
    }
)

panier, _ = Panier.objects.get_or_create(utilisateur=customer)
ArticlePanier.objects.filter(panier=panier).delete()
article = ArticlePanier.objects.create(panier=panier, produit=produit, quantite=2)

factory = APIRequestFactory()
commande_view = CommandeViewSet.as_view({'post': 'valider_panier'})
request = factory.post('/api/commandes/valider_panier/', {
    'adresse_livraison': '123 Rue Test, Dakar',
    'methode_paiement': 'wave',
    'mode_livraison': 'Standard',
    'prix_livraison': '200'
}, format='json')
force_authenticate(request, user=customer)
response = commande_view(request)
print('VALIDATION STATUS:', response.status_code)
print(response.data)

if response.status_code not in (200, 201):
    raise SystemExit('Validation du panier a échoué')

commande_id = response.data['commande']['id']
commande = Commande.objects.get(id=commande_id)
print('COMMANDE CREATED:', commande.numero, commande.statut, 'TOTAL', commande.montant_total)
print('CUSTOMER NOTIFS BEFORE:', Notification.objects.filter(utilisateur=customer, commande=commande).count())

vendor_request = factory.patch(
    f'/api/commandes/vendeur/commandes/{commande_id}/mettre_a_jour_statut/',
    {'statut': 'confirme'},
    format='json'
)
force_authenticate(vendor_request, user=vendor)

vendeur_view = CommandeVendeurViewSet.as_view({'patch': 'mettre_a_jour_statut'})
response2 = vendeur_view(vendor_request, pk=str(commande_id))
print('VENDOR UPDATE STATUS:', response2.status_code)
print(response2.data)

commande.refresh_from_db()
print('COMMANDE UPDATED:', commande.statut)
print('CUSTOMER NOTIFS AFTER:', Notification.objects.filter(utilisateur=customer, commande=commande).count())
for notif in Notification.objects.filter(utilisateur=customer, commande=commande):
    print('-', notif.titre, '|', notif.message, '| lu=', notif.est_lu)
