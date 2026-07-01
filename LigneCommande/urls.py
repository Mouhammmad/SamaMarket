from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.views import LigneCommandeViewSet

router = DefaultRouter()
router.register(r'lignes', LigneCommandeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
