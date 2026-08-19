from django.urls import path

from .views import (
    MaBoutiqueView,
    VueDetailBoutique,
    VueListeBoutiques,
    VueProduitsDeLaBoutique,
    VuePromotionsDeLaBoutique,
    VueAvisDeLaBoutique,
    VueCreerBoutique,
    ParametresBoutiqueView,
    SuivreBoutiqueView,
    StatutSuiviBoutiqueView,
)


urlpatterns = [

    # ----------------------------------------------------------
    # BOUTIQUES
    # ----------------------------------------------------------

    path(
        '',
        VueListeBoutiques.as_view(),
        name='boutique-list'
    ),

    path(
        'create/',
        VueCreerBoutique.as_view(),
        name='boutique-create'
    ),

    # ----------------------------------------------------------
    # MA BOUTIQUE
    # ----------------------------------------------------------

    path(
        'ma/',
        MaBoutiqueView.as_view(),
        name='ma-boutique'
    ),

    path(
        'ma-boutique/',
        MaBoutiqueView.as_view(),
        name='ma-boutique'
    ),

    # ----------------------------------------------------------
    # BOUTIQUE PUBLIQUE
    # ----------------------------------------------------------

    path(
        '<int:pk>/',
        VueDetailBoutique.as_view(),
        name='boutique-detail'
    ),

    path(
        '<int:pk>/produits/',
        VueProduitsDeLaBoutique.as_view(),
        name='boutique-produits'
    ),

    path(
        '<int:pk>/avis/',
        VueAvisDeLaBoutique.as_view(),
        name='boutique-avis'
    ),

    path(
        '<int:pk>/promotions/',
        VuePromotionsDeLaBoutique.as_view(),
        name='boutique-promotions'
    ),
    path(
    'ma/parametres/',
    ParametresBoutiqueView.as_view(),
    name='ma-boutique-parametres'
),
path(
    '<int:pk>/suivre/',
    SuivreBoutiqueView.as_view(),
    name='boutique-suivre'
),

path(
    '<int:pk>/suivi/',
    StatutSuiviBoutiqueView.as_view(),
    name='boutique-suivi-statut'
),
]