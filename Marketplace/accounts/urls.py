from django.urls import path
from .views import test_account

urlpatterns = [
    path('', test_account, name='accounts-test'),
]