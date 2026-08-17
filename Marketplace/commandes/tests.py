from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from boutiques.models import Boutique
from commandes.models import ArticlePanier, Commande, Panier
from commandes.views import CommandeViewSet, _calculer_reduction_promo
from produits.models import Categorie, Produit, Promotion

User = get_user_model()


class CommandePromoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='secret123')
        self.vendor = User.objects.create_user(username='vendor', email='vendor@example.com', password='secret123', role='VENDOR')
        self.boutique = Boutique.objects.create(
            responsable=self.vendor,
            nom='Boutique test',
            description='desc',
            ville='Dakar',
            apprové=True,
        )
        self.categorie = Categorie.objects.create(nom='Catégorie test', description='desc')
        self.produit = Produit.objects.create(
            boutique=self.boutique,
            categorie=self.categorie,
            nom='Produit test',
            description='desc',
            marque='Marca',
            sku='SKU-TEST',
            slug='produit-test',
            prix=Decimal('1000.00'),
            quantite_stock=10,
        )
        self.promotion = Promotion.objects.create(
            boutique=self.boutique,
            code='PROMO10',
            taux_remise=Decimal('10.00'),
            type_remise='pourcentage',
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=3),
            est_active=True,
            limite_usage=0,
        )
        self.promotion.produits.add(self.produit)
        self.panier = Panier.objects.create(utilisateur=self.user)
        ArticlePanier.objects.create(panier=self.panier, produit=self.produit, quantite=2)

    def test_calculer_reduction_promo_returns_discount(self):
        result = _calculer_reduction_promo(self.panier, 'PROMO10')

        self.assertTrue(result['applique'])
        self.assertEqual(result['reduction'], Decimal('200.00'))

    def test_valider_panier_creates_order_and_clears_cart(self):
        factory = APIRequestFactory()
        request = factory.post(
            '/api/commandes/commandes/valider_panier/',
            {
                'adresse_livraison': 'Dakar',
                'methode_paiement': 'wave',
                'code_promo': 'PROMO10',
            },
            format='json',
        )
        force_authenticate(request, user=self.user)

        response = CommandeViewSet.as_view({'post': 'valider_panier'})(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Commande.objects.count(), 1)
        self.assertFalse(self.panier.articles.exists())
