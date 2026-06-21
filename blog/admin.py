from django.contrib import admin
from .models import Post, Categorie, Produit, Commande, LigneCommande
from django.apps import apps

# Register your models here.
admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Post)
#pour recuperer tous les models definis dans mon application django
models = apps.get_models()

for model in models:
    try:
        #configuration dynamique de l'affichage pour lister tous les champs en colonnes
        class DynamicAdmin(admin.ModelAdmin):
            list_display= [field.name for field in model._meta.fields]


        #enregistrement du model avec sa configuration d'affichage
        admin.site.register(model, DynamicAdmin)

    except admin.sites.AlreadyRegistered:
        #ignore les modeles deja enregistrés par defaut comme User ou Group
        pass

