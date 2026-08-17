from rest_framework import serializers
from .models import Panier, ArticlePanier
from produits.models import Produit
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()

class ProduitResumSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        if obj.image:
            try:
                url = obj.image.url
            except ValueError:
                return None
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class ArticlePanierSerializer(serializers.ModelSerializer):
    produit = ProduitResumSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=Produit.objects.all(),
        source='produit',
        write_only=True
    )
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = ArticlePanier
        fields = ['id', 'produit', 'produit_id', 'quantite', 'sous_total', 'date_ajout']

    def get_sous_total(self, obj):
        return obj.obtenir_sous_total()


class PanierSerializer(serializers.ModelSerializer):
    articles = ArticlePanierSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'articles', 'total', 'date_mise_a_jour']

    def get_total(self, obj):
        return obj.obtenir_total()

from .models import Commande, LigneCommande, Paiement, Notification

class LigneCommandeSerializer(serializers.ModelSerializer):
    produit = ProduitResumSerializer(read_only=True)
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'quantite', 'prix_unitaire', 'total', 'sous_total']

    def get_sous_total(self, obj):
        return obj.calculer_sous_total()


class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    paiement = serializers.SerializerMethodField()
    mode_paiement = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    telephone = serializers.SerializerMethodField()
    nombre_produits = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    total = serializers.DecimalField(source='montant_total', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Commande
        fields = [
            'id',
            'numero',
            'statut',
            'sous_total',
            'frais_livraison',
            'reduction',
            'mode_livraison',
            'adresse_livraison',
            'notes',
            'lignes',
            'paiement',
            'mode_paiement',
            'client',
            'email',
            'telephone',
            'nombre_produits',
            'total',
            'date_creation',
            'date',
            'boutique'
        ]

    def get_paiement(self, obj):
        try:
            return PaiementSerializer(obj.paiement).data
        except Exception:
            return None

    def get_mode_paiement(self, obj):
        paiement = getattr(obj, 'paiement', None)
        return paiement.methode if paiement else None

    def get_client(self, obj):
        if obj.utilisateur:
            first_name = getattr(obj.utilisateur, 'first_name', '') or getattr(obj.utilisateur, 'prenom', '')
            last_name = getattr(obj.utilisateur, 'last_name', '') or getattr(obj.utilisateur, 'nom', '')
            return f"{first_name} {last_name}".strip() or obj.utilisateur.username
        return None

    def get_email(self, obj):
        return getattr(obj.utilisateur, 'email', None)

    def get_telephone(self, obj):
        return getattr(obj.utilisateur, 'telephone', None) or getattr(obj.utilisateur, 'phone', None)

    def get_nombre_produits(self, obj):
        total = obj.lignes.aggregate(total=Sum('quantite'))['total'] or 0
        return int(total)

    def get_date(self, obj):
        return obj.date_creation.strftime('%d/%m/%Y %H:%M') if obj.date_creation else None


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = ['id', 'montant', 'methode', 'statut', 'id_transaction', 'date_creation']

from .models import Livraison

class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = ['id', 'adresse', 'statut', 'numero_suivi', 'date_prevue', 'date_livraison']

class ClientCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "prenom",
            "nom",
            "email",
            "telephone"
        ]


class NotificationSerializer(serializers.ModelSerializer):
    date_creation = serializers.DateTimeField(format='%d/%m/%Y %H:%M', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'commande',
            'titre',
            'message',
            'type',
            'est_lu',
            'sms_envoye',
            'date_creation'
        ]