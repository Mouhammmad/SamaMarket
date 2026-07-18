from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from blog.views import CategorieViewSet, ProduitViewSet, CommandeViewSet, LigneCommandeViewSet
from django.conf.urls.static import static

routeur = DefaultRouter()
routeur.register(r'categories', CategorieViewSet)
routeur.register(r'produits', ProduitViewSet)
routeur.register(r'commandes', CommandeViewSet)
routeur.register(r'ligne',LigneCommandeViewSet )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(routeur.urls)),
    path('api/', include('Commande.urls')),
    path('', include('blog.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)