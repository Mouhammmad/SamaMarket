import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Marketplace.settings")
django.setup()

from comptes.models import User

username = os.getenv("ADMIN_USERNAME")
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")

if not username or not password:
    raise Exception("ADMIN_USERNAME ou ADMIN_PASSWORD manquant")

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email or "",
        "role": "ADMIN",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f"Administrateur {username} créé avec succès.")
else:
    user.role = "ADMIN"
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print(f"Administrateur {username} mis à jour avec succès.")