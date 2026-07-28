from django.urls import path

from .views import (
    VueCommandesRecents,
    VueGraphiqueRevenus,
    VueMettreAJourStatutCommandeVendeur,
    VueProduitsVendeur,
    VueStatistiquesVendeur,
    VueVentesParCategorie,
)

urlpatterns = [
    path('stats/', VueStatistiquesVendeur.as_view()),
    path('graphique-revenus/', VueGraphiqueRevenus.as_view()),
    path('categorie-vendeur/', VueVentesParCategorie.as_view()),
    path('commandes-recentes/', VueCommandesRecents.as_view()),
    path('produits/', VueProduitsVendeur.as_view()),
    path('commandes/<int:pk>/mettre_a_jour_statut/', VueMettreAJourStatutCommandeVendeur.as_view()),
]