from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VueListeProduits,
    VueDetailProduit,
    VueListeCategories,
    FavoriViewSet,
    AvisViewSet,
    PromotionViewSet,
    ProduitViewSet,
    ProduitVarianteViewSet
)
from .views import VendeurProduitViewSet


router = DefaultRouter()
router.register(r'favoris', FavoriViewSet, basename='favoris')
router.register(r'avis', AvisViewSet, basename='avis')
router.register(r'promotions', PromotionViewSet, basename='promotions')
router.register(r'produits', ProduitViewSet, basename='produits')
router.register(
    r'vendeur/produits',
    VendeurProduitViewSet,
    basename='vendeur-produits'
)
router.register(
    "vendeur/variantes",
    ProduitVarianteViewSet,
    basename="vendeur-variantes"
)
router.register(
    "vendeur/promotions",
    PromotionViewSet,
    basename="vendeur-promotions"
)
urlpatterns = [
    path('', VueListeProduits.as_view()),
    path('categories/', VueListeCategories.as_view()),
    path('<int:pk>/', VueDetailProduit.as_view(), name='produit-detail'),
    path('', include(router.urls)),
]
