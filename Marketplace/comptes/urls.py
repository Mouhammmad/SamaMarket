from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfilViewSet
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import test_account, RegisterView, LoginView


router = DefaultRouter()
router.register(r'profil', ProfilViewSet, basename='profil')

urlpatterns = [
    path('', include(router.urls)),
    path('', test_account, name='accounts-test'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
]
