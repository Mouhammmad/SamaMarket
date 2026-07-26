from django.contrib import admin
from .models import Categorie, Produit, Favori, Avis, Promotion

admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(Favori)
admin.site.register(Avis)
admin.site.register(Promotion)