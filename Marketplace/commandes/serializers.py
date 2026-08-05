from rest_framework import serializers
from .models import Panier, ArticlePanier
from produits.models import Produit
from django.contrib.auth import get_user_model

User = get_user_model()

class ProduitResumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'prix', 'image']


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

from .models import Commande, LigneCommande, Paiement

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
    client = ClientCommandeSerializer(
    source="utilisateur",
    read_only=True
)
    montant_total = serializers.ReadOnlyField()

    class Meta:
        model = Commande
        fields = ['id', 'numero', 'statut', "client", "montant_total", 'sous_total', 'adresse_livraison', 'notes', 'lignes', 'paiement', 'date_creation', 'boutique']

    def get_paiement(self, obj):
        try:
            return PaiementSerializer(obj.paiement).data
        except:
            return None


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
    prenom = serializers.CharField(source='first_name', read_only=True)
    nom = serializers.CharField(source='last_name', read_only=True)
    telephone = serializers.CharField(source='phone', read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "prenom",
            "nom",
            "email",
            "telephone"
        ]


class CommandeDetailVendeurSerializer(serializers.ModelSerializer):
    # flatten user info
    client = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    telephone = serializers.SerializerMethodField()
    # map lines to produits array expected by frontend
    produits = serializers.SerializerMethodField()
    mode_paiement = serializers.SerializerMethodField()
    paiement = serializers.SerializerMethodField()
    adresse = serializers.CharField(source='adresse_livraison', read_only=True)
    livraison = serializers.DecimalField(source='frais_livraison', max_digits=10, decimal_places=2, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            'id', 'numero', 'statut', 'client', 'email', 'telephone',
            'produits', 'adresse', 'mode_paiement', 'paiement',
            'sous_total', 'livraison', 'reduction', 'total', 'date_creation'
        ]

    def get_client(self, obj):
        u = obj.utilisateur
        name = (getattr(u, 'first_name', '') or '') + (' ' + (getattr(u, 'last_name','') or '') if getattr(u, 'last_name', '') else '')
        return name.strip() or getattr(u, 'username', '')

    def get_email(self, obj):
        return getattr(obj.utilisateur, 'email', None)

    def get_telephone(self, obj):
        return getattr(obj.utilisateur, 'phone', None)

    def get_produits(self, obj):
        items = []
        for line in obj.lignes.select_related('produit').all():
            p = line.produit
            items.append({
                'id': p.id,
                'nom': p.nom,
                'image': getattr(p.image, 'url', None) if getattr(p, 'image', None) else None,
                'quantite': line.quantite,
                'prix': str(line.prix_unitaire)
            })
        return items

    def get_mode_paiement(self, obj):
        try:
            return obj.paiement.methode
        except Exception:
            return None

    def get_paiement(self, obj):
        try:
            return PaiementSerializer(obj.paiement).data
        except Exception:
            return None

    def get_total(self, obj):
        try:
            return str(obj.montant_total)
        except Exception:
            return None