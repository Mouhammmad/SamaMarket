from django.db import models

class Commande(models.Model):
    CHOIX_STATUT = [
        ('En attente', 'En attente'),
        ('Payée', 'Payée'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée'),
    ]
    
    nom_client = models.CharField(max_length=255)
    email_client = models.EmailField()
    statut = models.CharField(max_length=20, choices=CHOIX_STATUT, default='EN_ATTENTE')
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.nom_client}"



