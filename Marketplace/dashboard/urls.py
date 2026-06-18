from django.urls import path
from .views import VendorDashboardView, AdminDashboardView

urlpatterns = [
    path('', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin-dashboard'),
]