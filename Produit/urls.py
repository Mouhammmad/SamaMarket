from django.urls import path,include
from rest_framework.routers import DefaultRouter
from blog.views import ProduitViewSet

router = DefaultRouter()
router.register(r'produits', ProduitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
