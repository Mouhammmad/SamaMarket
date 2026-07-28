from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from boutiques.models import Boutique
from commandes.models import Commande, LigneCommande
from produits.models import Category, Produit

User = get_user_model()


class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de démonstration pour les endpoints vendeur.'

    def handle(self, *args, **options):
        vendeur, _ = User.objects.get_or_create(
            username='vendeur1',
            defaults={'email': 'vendeur1@example.com', 'role': 'VENDOR'}
        )
        vendeur.set_password('vendeur123')
        vendeur.is_staff = True
        vendeur.is_superuser = True
        vendeur.save()

        boutique, _ = Boutique.objects.get_or_create(
            owner=vendeur,
            defaults={
                'nom': 'Boutique Test',
                'description': 'Boutique de démonstration',
                'ville': 'Dakar',
                'logo': 'boutiques/default.png',
                'rating': 4.5,
                'followers': 12,
                'sales': 3,
                'approved': True,
            },
        )

        categorie, _ = Category.objects.get_or_create(nom='Électronique')

        produit, created = Produit.objects.get_or_create(
            nom='Smartphone Demo',
            defaults={
                'boutique': boutique,
                'categorie': categorie,
                'description': 'Produit de démonstration',
                'prix': 299.99,
                'stock': 10,
                'image': 'products/demo.jpg',
                'active': True,
            },
        )

        client, _ = User.objects.get_or_create(
            username='client1',
            defaults={'email': 'client1@example.com', 'role': 'CUSTOMER'}
        )
        client.set_password('client123')
        client.save()

        commande, _ = Commande.objects.get_or_create(
            id=1001,
            defaults={
                'utilisateur': client,
                'montant_total': 299.99,
                'statut': 'livre',
                'adresse_livraison': 'Adresse de démonstration',
                'notes': 'Commande de démonstration',
            },
        )

        LigneCommande.objects.get_or_create(
            commande=commande,
            produit=produit,
            defaults={
                'quantite': 1,
                'prix_unitaire': 299.99,
            },
        )

        commande2, _ = Commande.objects.get_or_create(
            id=1002,
            defaults={
                'utilisateur': client,
                'montant_total': 159.90,
                'statut': 'en_attente',
                'adresse_livraison': 'Adresse de démonstration',
                'notes': 'Commande de démonstration',
            },
        )

        LigneCommande.objects.get_or_create(
            commande=commande2,
            produit=produit,
            defaults={
                'quantite': 1,
                'prix_unitaire': 159.90,
            },
        )

        self.stdout.write(self.style.SUCCESS('Données de démonstration ajoutées avec succès.'))
