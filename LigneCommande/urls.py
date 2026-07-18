from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.views import LigneCommandeViewSet

router = DefaultRouter()
router.register(r'ligne', LigneCommandeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
