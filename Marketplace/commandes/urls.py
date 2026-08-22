from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PanierViewSet, CommandeViewSet, LivraisonViewSet, CommandeVendeurViewSet, AdminCommandeViewSet

router = DefaultRouter()
router.register(r'panier', PanierViewSet, basename='panier')
router.register(r'commandes', CommandeViewSet, basename='commandes')
router.register(r'livraisons', LivraisonViewSet, basename='livraisons')
router.register(r'admin/commandes', AdminCommandeViewSet, basename='admin-commandes')
router.register(r'vendeur/commandes', CommandeVendeurViewSet, basename='vendeur-commandes')

urlpatterns = [
    path('', include(router.urls)),
]