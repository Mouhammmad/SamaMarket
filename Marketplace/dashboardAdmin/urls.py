from django.urls import path

from .views import AdminDashboardStats

urlpatterns = [
    path('stats/', AdminDashboardStats.as_view()),
]