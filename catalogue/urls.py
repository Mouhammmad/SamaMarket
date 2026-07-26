from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriViewSet, AvisViewSet, PromotionViewSet, ProduitViewSet

router = DefaultRouter()
router.register(r'favoris', FavoriViewSet, basename='favoris')
router.register(r'avis', AvisViewSet, basename='avis')
router.register(r'promotions', PromotionViewSet, basename='promotions')
router.register(r'produits', ProduitViewSet, basename='produits')

urlpatterns = [
    path('', include(router.urls)),
]