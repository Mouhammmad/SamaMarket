from django.urls import path

from .views import VueUtilisateursRecents, VueListeUtilisateurs, VueVendeursEnAttente, VueStatistiquesAdmin, VueDetailUtilisateur, VueExportCommandesAdmin, VueGestionUtilisateur, VueListeBoutiques, VueDetailBoutique, VueParametresPlateforme, VueCreationAdmin


urlpatterns = [
    path('parametres/', VueParametresPlateforme.as_view()),
    path('admins/', VueCreationAdmin.as_view()),
    path('stats/', VueStatistiquesAdmin.as_view()),
    path('vendeur_en_attente/', VueVendeursEnAttente.as_view()),
    path('utilisateurs_recents/', VueUtilisateursRecents.as_view()),
    path(
    "utilisateurs/",
    VueListeUtilisateurs.as_view()
),
path(
    "boutiques/<int:pk>/",
    VueDetailBoutique.as_view()
),
path(
    "utilisateurs/<int:pk>/",
    VueDetailUtilisateur.as_view()
),
path(
    "utilisateurs/<int:pk>/gestion/",
    VueGestionUtilisateur.as_view()
),
path(
    "boutiques/",
    VueListeBoutiques.as_view()
),

]