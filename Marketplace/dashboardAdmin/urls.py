from django.urls import path

from .views import VueUtilisateursRecents, VueVendeursEnAttente, VueStatistiquesAdmin

urlpatterns = [
    path('stats/', VueStatistiquesAdmin.as_view()),
    path('vendeur_en_attente/', VueVendeursEnAttente.as_view()),
    path('utilisateurs_recents/', VueUtilisateursRecents.as_view()),
]