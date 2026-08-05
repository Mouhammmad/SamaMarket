import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Marketplace.settings')
django.setup()

from comptes.models import User

vendors = User.objects.filter(role='VENDOR')
print(f"✅ Vendeurs trouvés: {vendors.count()}")
for u in vendors[:5]:
    boutique = getattr(u, 'boutique', None)
    print(f"  - {u.username} ({u.email}) - Boutique: {boutique.nom if boutique else 'AUCUNE'}")
    
if vendors.count() == 0:
    print("\n⚠️  Aucun vendeur trouvé!")
