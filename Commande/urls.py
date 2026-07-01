from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommandeViewSet

routeur = DefaultRouter()
routeur.register(r'commandes', CommandeViewSet)

urlpatterns = [
    path('', include(routeur.urls)),
]
