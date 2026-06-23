from django.urls import path
from .views import VendeurDashboardStats

urlpatterns = [
    path('stats/', VendeurDashboardStats.as_view()),
   
]