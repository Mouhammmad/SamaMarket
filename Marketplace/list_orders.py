import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()
from commandes.models import Commande
from comptes.models import User

user = User.objects.filter(username='vendeur_test').first()
if not user:
    print('Utilisateur vendeur_test introuvable')
else:
    commandes = Commande.objects.filter(boutique__responsable=user)
    if not commandes.exists():
        print('Aucune commande pour ce vendeur')
    else:
        for c in commandes:
            print(c.id, c.numero, c.statut, getattr(c.boutique, 'nom', None), getattr(c.utilisateur, 'username', None), 'lignes:', c.lignes.count())
