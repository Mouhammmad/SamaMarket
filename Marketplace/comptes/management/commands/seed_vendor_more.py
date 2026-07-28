from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date

from boutiques.models import Boutique
from produits.models import Category, Produit
from commandes.models import Commande, LigneCommande

User = get_user_model()


class Command(BaseCommand):
    help = 'Ajoute des commandes de démonstration réparties sur les 6 derniers mois pour le vendeur1'

    def handle(self, *args, **options):
        vendeur = User.objects.filter(username='vendeur1').first()
        if not vendeur:
            self.stdout.write(self.style.ERROR('vendeur1 introuvable. Exécutez seed_demo_data d\'abord.'))
            return

        boutique = Boutique.objects.filter(owner=vendeur).first()
        if not boutique:
            self.stdout.write(self.style.ERROR('Boutique pour vendeur1 introuvable.'))
            return

        client = User.objects.filter(username='client1').first()
        if not client:
            client = User.objects.create(username='client1', email='client1@example.com', role='CUSTOMER')
            client.set_password('client123')
            client.save()

        # categories et produits
        cat_mode, _ = Category.objects.get_or_create(nom='Mode')
        cat_elec, _ = Category.objects.get_or_create(nom='Électronique')
        cat_food, _ = Category.objects.get_or_create(nom='Alimentation')

        prod_mode, _ = Produit.objects.get_or_create(nom='Robe Demo', defaults={
            'boutique': boutique,
            'categorie': cat_mode,
            'description': 'Robe style local',
            'prix': Decimal('25.00'),
            'stock': 20,
            'image': 'products/robe_demo.jpg',
            'active': True,
        })

        prod_phone, _ = Produit.objects.get_or_create(nom='Téléphone Demo', defaults={
            'boutique': boutique,
            'categorie': cat_elec,
            'description': 'Téléphone de démonstration',
            'prix': Decimal('199.99'),
            'stock': 5,
            'image': 'products/phone_demo.jpg',
            'active': True,
        })

        prod_honey, _ = Produit.objects.get_or_create(nom='Miel Local', defaults={
            'boutique': boutique,
            'categorie': cat_food,
            'description': 'Miel produit local',
            'prix': Decimal('9.90'),
            'stock': 50,
            'image': 'products/honey_demo.jpg',
            'active': True,
        })

        today = timezone.now().date()
        # first day of current month
        def month_start(dt, months_ago):
            y = dt.year
            m = dt.month - months_ago
            while m <= 0:
                m += 12
                y -= 1
            return date(y, m, 1)

        created_orders = 0

        for months_ago in range(0, 6):
            ms = month_start(today, months_ago)
            # create 1-3 orders per month
            for j in range(1, 2 + (months_ago % 3)):
                ord_date = ms + timedelta(days=2 + j)
                order = Commande.objects.create(
                    utilisateur=client,
                    montant_total=Decimal('0.00'),
                    statut='livre' if (j % 2 == 0) else 'en_attente',
                    adresse_livraison='Adresse de démonstration',
                    notes='',
                    date_creation=ord_date
                )

                # add items rotating categories
                if j % 3 == 0:
                    prod = prod_honey
                    qty = 3
                elif j % 2 == 0:
                    prod = prod_phone
                    qty = 1
                else:
                    prod = prod_mode
                    qty = 2

                price = prod.prix * qty
                LigneCommande.objects.create(commande=order, produit=prod, quantite=qty, prix_unitaire=price)

                # update total
                order.montant_total = price
                order.save(update_fields=['montant_total'])
                created_orders += 1

        self.stdout.write(self.style.SUCCESS(f'Ajouté {created_orders} commandes réparties sur 6 mois.'))
