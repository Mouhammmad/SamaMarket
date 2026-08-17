from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from boutiques.models import Boutique
from comptes.models import User
from .models import Categorie, Produit, Favori, Avis


class ProduitDetailApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='tester', password='secret123')
        self.categorie = Categorie.objects.create(nom='Électronique')
        self.boutique = Boutique.objects.create(
            responsable=self.user,
            nom='Boutique Test',
            description='Boutique de test',
            ville='Dakar'
        )
        self.produit = Produit.objects.create(
            boutique=self.boutique,
            categorie=self.categorie,
            nom='Smartphone Test',
            description='Description test',
            prix=15000,
            quantite_stock=10,
            est_actif=True,
        )

    def test_retrieves_product_detail(self):
        response = self.client.get(reverse('produit-detail', kwargs={'pk': self.produit.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['nom'], 'Smartphone Test')
        self.assertEqual(response.json()['prix'], '15000.00')

    def test_exposes_stock_status_and_favorite_state(self):
        self.produit.quantite_stock = 0
        self.produit.save(update_fields=['quantite_stock'])
        Favori.objects.create(utilisateur=self.user, produit=self.produit)
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse('produit-detail', kwargs={'pk': self.produit.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['disponible'])
        self.assertEqual(response.json()['stock_status'], 'rupture')
        self.assertTrue(response.json()['est_favori'])

    def test_vendeur_receives_reviews_for_his_products(self):
        vendeur = User.objects.create_user(username='vendeur_test', password='secret123', role='VENDOR')
        boutique_vendeur = Boutique.objects.create(
            responsable=vendeur,
            nom='Boutique Vendeur',
            description='Boutique du vendeur',
            ville='Thiès'
        )
        produit_vendeur = Produit.objects.create(
            boutique=boutique_vendeur,
            categorie=self.categorie,
            nom='Produit vendeur',
            description='Produit du vendeur',
            prix=20000,
            quantite_stock=10,
            slug='produit-vendeur-avis-unique',
            sku='SKU-VENDEUR-AVIS-UNIQUE',
            est_actif=True,
        )

        client = User.objects.create_user(username='client_avis', password='secret123', role='CUSTOMER')
        avis = Avis.objects.create(
            utilisateur=client,
            produit=produit_vendeur,
            note=5,
            commentaire='Très bon produit'
        )

        self.client.force_authenticate(vendeur)
        response = self.client.get('/api/produits/avis/?vendeur=true')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['id'], avis.id)
        self.assertEqual(response.json()[0]['commentaire'], 'Très bon produit')
