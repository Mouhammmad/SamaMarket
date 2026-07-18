from rest_framework import serializers
from blog.models import Commande, LigneCommande

class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, source='lignescommande')
    class Meta:
        model = Commande 
        fields = ['id','client', 'lignes'] 
      
    def create(self, donnees_validees):
        # Extraction des produit pour enregistrer la commande principale d'abord
        donnees_ligne = donnees_validees.pop('lignes', [])
        
        commande = Commande.objects.create(**donnees_validees)
        
        # Enregistrement de chaque produit lié à cette commande
        for donnee_individuelle in donnees_ligne:
            LigneCommande.objects.create(commande=commande, **donnee_individuelle)
        return commande
    
    def update(self, instance, donnees_validees):
        donnees_ligne = donnees_validees.pop('lignescommande', donnees_validees.pop('lignes'),None)

        for attr, value in donnees_validees.items():
            setattr(instance, attr, value)
        instance.save()

        if donnees_ligne is not None:

           LigneCommande.objects.filter(commande=instance).delete()

           for donnee_individuelle in donnees_ligne:
               LigneCommande.objects.create(commande=instance, **donnee_individuelle)

        return instance
