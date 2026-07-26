from django.contrib import admin
from .models import Panier, ArticlePanier, Commande, LigneCommande, Paiement, Livraison

admin.site.register(Panier)
admin.site.register(ArticlePanier)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Paiement)
admin.site.register(Livraison)