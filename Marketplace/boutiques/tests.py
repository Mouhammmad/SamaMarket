from django.contrib.auth import get_user_model
from django.test import TestCase

from produits.models import Avis, Categorie, Produit
from .models import Boutique
from .serializers import BoutiqueSerializer


class BoutiqueSerializerTests(TestCase):
    def test_serializer_exposes_approved_field(self):
        user = get_user_model().objects.create_user(
            username='vendor',
            email='vendor@example.com',
            password='secret123'
        )
        boutique = Boutique.objects.create(
            responsable=user,
            nom='Ma boutique',
            description='Description',
            ville='Dakar'
        )

        serializer = BoutiqueSerializer(boutique)

        self.assertIn('apprové', serializer.data)
        self.assertFalse(serializer.data['apprové'])

    def test_serializer_exposes_dynamic_store_metrics(self):
        user = get_user_model().objects.create_user(
            username='vendor2',
            email='vendor2@example.com',
            password='secret123'
        )
        boutique = Boutique.objects.create(
            responsable=user,
            nom='Boutique dynamique',
            description='Description',
            ville='Dakar',
            apprové=True,
            followers=54
        )
        categorie = Categorie.objects.create(nom='Électronique')
        produit_1 = Produit.objects.create(
            boutique=boutique,
            categorie=categorie,
            nom='Produit A',
            prix=100,
            quantite_stock=10,
            slug='produit-a-1',
            sku='SKU-A-1'
        )
        produit_2 = Produit.objects.create(
            boutique=boutique,
            categorie=categorie,
            nom='Produit B',
            prix=200,
            quantite_stock=5,
            slug='produit-b-2',
            sku='SKU-B-2'
        )

        reviewer_1 = get_user_model().objects.create_user(
            username='reviewer1',
            email='reviewer1@example.com',
            password='secret123'
        )
        reviewer_2 = get_user_model().objects.create_user(
            username='reviewer2',
            email='reviewer2@example.com',
            password='secret123'
        )
        reviewer_3 = get_user_model().objects.create_user(
            username='reviewer3',
            email='reviewer3@example.com',
            password='secret123'
        )

        Avis.objects.create(utilisateur=reviewer_1, produit=produit_1, note=5, est_approuve=True)
        Avis.objects.create(utilisateur=reviewer_2, produit=produit_1, note=4, est_approuve=True)
        Avis.objects.create(utilisateur=reviewer_3, produit=produit_2, note=1, est_approuve=False)

        serializer = BoutiqueSerializer(boutique)

        self.assertEqual(serializer.data['nombre_produits'], 2)
        self.assertEqual(serializer.data['nombre_avis'], 2)
        self.assertEqual(serializer.data['note'], 4.5)
        self.assertEqual(serializer.data['followers'], 54)
        self.assertTrue(serializer.data['verifie'])
        self.assertIn('categories', serializer.data)
        self.assertEqual(serializer.data['categories'][0]['nom'], 'Électronique')
        self.assertEqual(serializer.data['repartition_notes'][5], 1)
        self.assertEqual(serializer.data['repartition_notes'][4], 1)
