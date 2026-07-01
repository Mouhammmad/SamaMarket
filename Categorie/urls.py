from rest_framework.routers import DefaultRouter
from Categorie.views import CategorieViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'categories', CategorieViewSet)

urlpatterns = [
    path('', include(router.urls))
]