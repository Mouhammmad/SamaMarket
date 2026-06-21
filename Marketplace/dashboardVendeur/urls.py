from django.urls import path
from .views import VendorDashboardView

urlpatterns = [
    path('', VendorDashboardView.as_view(), name='vendor-dashboard'),
   
]