"""
URL configuration for Marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenRefreshView
from comptes.views import LoginView


def home(request):
    return JsonResponse({"message": "Bienvenue sur SamaMarket API"})


urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/token/', csrf_exempt(LoginView.as_view()), name='token_obtain_pair'),
    path('api/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    path('api/comptes/', include('comptes.urls')),
    path('api/commandes/', include('commandes.urls')),
    path('api/produits/', include('produits.urls')),
    path('api/boutiques/', include('boutiques.urls')),
    path('api/dashboard/admin/', include('dashboardAdmin.urls')),
    path('api/dashboard/vendeur/', include('dashboardVendeur.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)