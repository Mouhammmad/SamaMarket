import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from comptes.models import User

username = os.getenv("ADMIN_USERNAME")

try:
    user = User.objects.get(username=username)

    print("========== VERIFICATION ADMIN ==========")
    print("Utilisateur trouvé :", True)
    print("Username :", user.username)
    print("Role :", user.role)
    print("is_active :", user.is_active)
    print("is_staff :", user.is_staff)
    print("is_superuser :", user.is_superuser)
    print("========================================")

except User.DoesNotExist:
    print("========== VERIFICATION ADMIN ==========")
    print("Utilisateur trouvé :", False)
    print("========================================")