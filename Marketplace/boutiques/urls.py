from django.urls import path
from .views import (
    MaBoutiqueView,
    VueDetailBoutique,
    VueListeBoutiques,
    VueProduitsDeLaBoutique,
    VuePromotionsDeLaBoutique,
    VueAvisDeLaBoutique,
    VueCreerBoutique,
)

urlpatterns = [
    path('', VueListeBoutiques.as_view(), name='boutique-list'),
    path('create/', VueCreerBoutique.as_view(), name='boutique-create'),
    path('<int:pk>/', VueDetailBoutique.as_view(), name='boutique-detail'),


    path('<int:pk>/produits/', VueProduitsDeLaBoutique.as_view(), name='boutique-produits'),
    path('<int:pk>/avis/', VueAvisDeLaBoutique.as_view(), name='boutique-avis'),
    path('ma-boutique/', MaBoutiqueView.as_view(), name='ma-boutique'),
    path('ma/', MaBoutiqueView.as_view(), name='ma-boutique'),
    path('<int:pk>/promotions/', VuePromotionsDeLaBoutique.as_view(), name='boutique-promotions'),
]
