from django.contrib import admin
from django.apps import apps
from django.contrib.auth.apps import AuthConfig
from .models import Categorie, Produit, Commande, LigneCommande

# Changer le nom de l'application 
AuthConfig.verbose_name = "Gestion des accès"
# Changer le nom des modèles internes (Groupes et Utilisateurs)
apps.get_model('auth','Group')._meta.verbose_name= 'Groupe de rôle'
apps.get_model('auth','Group')._meta.verbose_name_plural= 'Groupe des rôles'
apps.get_model('auth','User')._meta.verbose_name= 'Compte utilisateur'
apps.get_model('auth','User')._meta.verbose_name_plural= 'Comptes utilisateurs'
# Pour  personnaliser l'affichage d'un modèle
admin.site.site_header = "Mon Administration E-Commerce"
admin.site.site_title = "E-commerce Admin"
admin.site.index_title = "Bienvenue sur la  gestion de votre boutique SamaMarket"


admin.site.register(Categorie)
admin.site.register(LigneCommande)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom','categorie', 'prix','stock', 'disponible']
    #permet de modifier le stock et le statut en un clic
    list_editable = ['stock' ]
    search_fields = ['nom']
    list_filter = ['categorie', 'disponible']
    
     # Gère la page détaillée de modification du produit
    def save_model(self, request, obj, form, change):
        if obj.stock == 0:
            obj.disponible = False
        else:
            obj.disponible = True
        super().save_model(request, obj, form, change)

class LigneCommandeInline(admin.TabularInline):
    model= LigneCommande
    extra = 0
    fields = ['produit','prix_unitaire','quantite']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    #liste des colonnes visibles directement dans le tableau
    list_display = ['id','obtenir_client','statut', 'total','paye','cree_le']
    #Permet de filtrer par statut et date
    list_filter = ['statut','paye','cree_le']
    list_editable = ['statut'] # Pour changer le statut en un clic !
    inlines =[LigneCommandeInline]

    #L'affichage de la page commande
    def save_model(self,request,obj, form, change):
        if obj.statut in ['Payée', 'Livrée']:
            obj.paye = True #met la coche bleue automatiquement
        else:
            obj.paye =  False # Met la croix rouge automatiquement ('En attente' ou 'Annulée')
        super().save_model(request, obj, form, change)

    #Calcul et affichage automatique du total après enregistrement des articles
    def save_formset(self, request, form, formset,change):
        super().save_formset(request,form, formset, change)
        commande = formset.instance
        # On calcule la somme directement depuis les lignes du formulaire
        total_commande = 0
        for ligne in commande.lignes.all():
            total_commande += ligne.obtenir_cout_total()
        commande.total = total_commande
        commande.save()

    #Fonction pour afficher le nom de l'utilisateur dans le tableau
    def obtenir_client(self,obj):
       return obj.client.username
    obtenir_client.short_description = 'Client'



   

