import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User

# Créer ou mettre à jour un utilisateur de test
username = 'vendeur_test'
email = 'vendeur_test@test.com'
password = 'Test1234'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'role': 'VENDOR',
        'first_name': 'Vendeur',
        'last_name': 'Test'
    }
)

# Toujours mettre à jour le mot de passe
user.set_password(password)
user.save()

print(f"{'✅ Créé' if created else '✅ Déjà existant'}: {username}")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Role: {user.role}")

# Vérifier la boutique
boutique = getattr(user, 'boutique', None)
print(f"   Boutique: {boutique.nom if boutique else 'À créer lors du premier accès'}")
