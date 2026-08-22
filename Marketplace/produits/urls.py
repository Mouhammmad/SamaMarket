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
from .views import CategorieViewSet
from .views import VueListeOffres
from .views import AdminProduitViewSet
router = DefaultRouter()
router.register(r'favoris', FavoriViewSet, basename='favoris')
router.register(r'avis', AvisViewSet, basename='avis')
router.register(
    r'admin/produits',
    AdminProduitViewSet,
    basename='admin-produits'
)
router.register(r'promotions', PromotionViewSet, basename='promotions')
router.register(r'produits', ProduitViewSet, basename='produits')
router.register(
    r'vendeur/produits',
    VendeurProduitViewSet,
    basename='vendeur-produits'
)
router.register(

    "categories",

    CategorieViewSet,

    basename="categories"

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
    path('offres/', VueListeOffres.as_view(), name='offres'),
]
