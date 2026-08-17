from rest_framework.test import APIRequestFactory, force_authenticate
from produits.views import AvisViewSet
from django.contrib.auth import get_user_model
import traceback
User=get_user_model()
u=User.objects.get(id=27)
factory=APIRequestFactory()
req=factory.get('/api/produits/avis/')
force_authenticate(req, user=u)
try:
    resp = AvisViewSet.as_view({'get':'list'})(req)
    print('resp', type(resp), getattr(resp, 'status_code', None))
    try:
        print('data', resp.data)
    except Exception:
        print('content', getattr(resp, 'content', None))
except Exception:
    traceback.print_exc()
