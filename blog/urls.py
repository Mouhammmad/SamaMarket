from django.urls import path
from blog.views import home, about, contact
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet, CategorieViewSet, CommandeViewSet

routeur = DefaultRouter()
routeur.register(r'produits', ProduitViewSet)
routeur.register(r'categories', CategorieViewSet)
routeur.register(r'commandes', CommandeViewSet)


urlpatterns=[
  path('',home),
  path('about/', about),
  path('contact/',contact),
  path('', include(routeur.urls)),
]