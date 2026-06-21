from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import test_account, RegisterView, LoginView

urlpatterns = [
    path('', test_account, name='accounts-test'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
]