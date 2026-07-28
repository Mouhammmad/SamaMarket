from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from boutiques.models import Boutique
from .models import Categorie, Produit


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
