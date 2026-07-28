from django.contrib.auth import get_user_model

User = get_user_model()

# Chercher l'admin existant
admin_users = User.objects.filter(role='ADMIN')
print(f"Utilisateurs ADMIN: {admin_users.count()}")
for user in admin_users:
    print(f"  - {user.username} ({user.email})")

# Créer un admin test s'il n'existe pas
if not admin_users.exists():
    admin = User.objects.create_user(
        username='admin',
        email='admin@sama.local',
        password='Admin123',
        role='ADMIN'
    )
    print(f"\nAdmin créé: {admin.username}")
else:
    print("\nAdmin existe déjà")
