from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.views import CommandeViewSet, AjouterLigneCommandeView

routeur = DefaultRouter()
routeur.register(r'commandes', CommandeViewSet)

urlpatterns = [
    path('', include(routeur.urls)),
    path('commandes/<int:pk>/ajouter-lignes', AjouterLigneCommandeView.as_view(), name='ajouter_lignes'),
]
