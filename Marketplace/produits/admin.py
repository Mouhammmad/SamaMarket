from django.contrib import admin
from .models import Produit, Categorie, Favori, Avis, Promotion


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'parent')
    search_fields = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prix', 'quantite_stock', 'categorie', 'boutique', 'est_actif', 'date_creation')
    list_filter = ('est_actif', 'categorie', 'boutique')
    search_fields = ('nom', 'description')
    ordering = ('-date_creation',)


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'produit', 'date_ajout')


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'produit', 'note', 'est_approuve')
    list_filter = ('est_approuve',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'boutique', 'taux_remise', 'type_remise', 'est_active')
    list_filter = ('est_active',)
