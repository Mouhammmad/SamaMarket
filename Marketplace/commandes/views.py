from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import uuid
from django.db.models import Sum
from .models import Panier, ArticlePanier, Commande, LigneCommande, Paiement, Livraison
from .serializers import (
    PanierSerializer, ArticlePanierSerializer,
    CommandeSerializer, LivraisonSerializer
)


class PanierViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_panier(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        return panier

    @action(detail=False, methods=['get'])
    def mon_panier(self, request):
        panier = self.get_panier(request)
        serializer = PanierSerializer(panier)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ajouter(self, request):
        panier = self.get_panier(request)
        serializer = ArticlePanierSerializer(data=request.data)
        if serializer.is_valid():
            produit = serializer.validated_data['produit']
            quantite = serializer.validated_data.get('quantite', 1)
            article, created = ArticlePanier.objects.get_or_create(
                panier=panier,
                produit=produit
            )
            if not created:
                article.quantite += quantite
            else:
                article.quantite = quantite
            article.save()
            return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'])
    def modifier_quantite(self, request):
        panier = self.get_panier(request)
        article_id = request.data.get('article_id')
        quantite = request.data.get('quantite')
        try:
            article = ArticlePanier.objects.get(id=article_id, panier=panier)
            if quantite <= 0:
                article.delete()
            else:
                article.quantite = quantite
                article.save()
            return Response(PanierSerializer(panier).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def supprimer_article(self, request):
        panier = self.get_panier(request)
        article_id = request.data.get('article_id')
        try:
            article = ArticlePanier.objects.get(id=article_id, panier=panier)
            article.delete()
            return Response(PanierSerializer(panier).data)
        except ArticlePanier.DoesNotExist:
            return Response({'erreur': 'Article introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def vider(self, request):
        panier = self.get_panier(request)
        panier.articles.all().delete()
        return Response({'message': 'Panier vidé'})


class CommandeViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Commande.objects.filter(utilisateur=self.request.user)

    @action(detail=False, methods=['post'])
    def valider_panier(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        if not panier.articles.exists():
            return Response({'erreur': 'Panier vide'}, status=status.HTTP_400_BAD_REQUEST)

        adresse = request.data.get('adresse_livraison')
        methode = request.data.get('methode_paiement')

        if not adresse:
            return Response({'erreur': 'Adresse de livraison requise'}, status=status.HTTP_400_BAD_REQUEST)

        if methode not in ['wave', 'orange_money']:
            return Response({'erreur': 'Méthode de paiement invalide'}, status=status.HTTP_400_BAD_REQUEST)

        commande = Commande.objects.create(
            utilisateur=request.user,
            adresse_livraison=adresse,
            sous_total=panier.obtenir_total(),
            boutique=panier.articles.first().produit.boutique,
            frais_livraison=0,
            reduction=0,
        )

        for article in panier.articles.all():
            if article.quantite > article.produit.quantite_stock:
                return Response(
                    {'erreur': f"Stock insuffisant pour {article.produit.nom}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            LigneCommande.objects.create(
                commande=commande,
                produit=article.produit,
                quantite=article.quantite,
                prix_unitaire=article.produit.prix,
                total=article.quantite * article.produit.prix,
            )

            produit = article.produit

            produit.quantite_stock -= article.quantite

            produit.save(
                update_fields=["quantite_stock"]
            )
            Paiement.objects.create(
                commande=commande,
                montant=commande.montant_total,
                methode=methode,
            )

        panier.articles.all().delete()

        return Response({
            'message': 'Commande créée avec succès',
            'commande': CommandeSerializer(commande).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def confirmer_paiement(self, request, pk=None):
        try:
            commande = Commande.objects.get(id=pk, utilisateur=request.user)
            paiement = commande.paiement
            id_transaction = request.data.get('id_transaction')

            if not id_transaction:
                return Response({'erreur': 'ID transaction requis'}, status=status.HTTP_400_BAD_REQUEST)

            paiement.id_transaction = id_transaction
            paiement.statut = 'complete'
            paiement.save()

            commande.statut = 'confirme'
            commande.save()

            return Response({
                'message': 'Paiement confirmé',
                'commande': CommandeSerializer(commande).data
            })
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def mes_commandes(self, request):
        assert request is not None
        commandes = self.get_queryset()
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)
    

class LivraisonViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def creer(self, request):
        commande_id = request.data.get('commande_id')
        try:
            commande = Commande.objects.get(id=commande_id, utilisateur=request.user)
            if commande.statut != 'confirme':
                return Response({'erreur': 'La commande doit être confirmée'}, status=status.HTTP_400_BAD_REQUEST)
            if hasattr(commande, 'livraison'):
                return Response({'erreur': 'Une livraison existe déjà pour cette commande'}, status=status.HTTP_400_BAD_REQUEST)

            livraison = Livraison.objects.create(
                commande=commande,
                adresse=commande.adresse_livraison,
                numero_suivi = (
                                "SAMA-"
                                 + uuid.uuid4().hex[:8].upper()
             ),      
                date_prevue=request.data.get('date_prevue')
            )
            commande.statut = 'expedie'
            commande.save()

            return Response(LivraisonSerializer(livraison).data, status=status.HTTP_201_CREATED)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def suivre(self, request):
        numero_suivi = request.query_params.get('numero_suivi')
        try:
            livraison = Livraison.objects.get(numero_suivi=numero_suivi)
            return Response(LivraisonSerializer(livraison).data)
        except Livraison.DoesNotExist:
            return Response({'erreur': 'Livraison introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def mettre_a_jour_statut(self, request, pk=None):
        try:
            livraison = Livraison.objects.get(id=pk)
            nouveau_statut = request.data.get('statut')
            if nouveau_statut not in dict(Livraison.STATUT_CHOICES):
                return Response({'erreur': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

            livraison.statut = nouveau_statut
            if nouveau_statut == 'livre':
                livraison.date_livraison = timezone.now()
                livraison.commande.statut = 'livre'
                livraison.commande.save()
            livraison.save()

            return Response(LivraisonSerializer(livraison).data)
        except Livraison.DoesNotExist:
            return Response({'erreur': 'Livraison introuvable'}, status=status.HTTP_404_NOT_FOUND)


class CommandeVendeurViewSet(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Commande.objects.filter(
            lignes__produit__boutique__responsable=self.request.user
        ).distinct()

    @action(detail=False, methods=['get'])
    def mes_commandes(self, request):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        commandes = self.get_queryset()
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def mettre_a_jour_statut(self, request, pk=None):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            commande = Commande.objects.get(
                id=pk,
                lignes__produit__boutique__responsable=request.user
            )
            nouveau_statut = request.data.get('statut')
            if nouveau_statut not in dict(Commande.STATUT_CHOICES):
                return Response({'erreur': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

            commande.statut = nouveau_statut
            commande.save()
            return Response(CommandeSerializer(commande).data)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def detail_commande(self, request, pk=None):
        if request.user.role.upper() not in {'VENDOR', 'ADMIN'}:
            return Response({'erreur': 'Accès réservé aux vendeurs'}, status=status.HTTP_403_FORBIDDEN)
        try:
            commande = Commande.objects.get(
                id=pk,
                lignes__produit__boutique__responsable=request.user
            )
            from .serializers import CommandeDetailVendeurSerializer
            return Response(CommandeDetailVendeurSerializer(commande).data)
        except Commande.DoesNotExist:
            return Response({'erreur': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        assert request is not None
        commandes = self.get_queryset()

        total = commandes.count()

        en_attente = commandes.filter(
            statut='en_attente'
            ).count()

        confirmees = commandes.filter(
        statut='confirme'
        ).count()

        expediees = commandes.filter(
        statut='expedie'
        ).count()

        livrees = commandes.filter(
        statut='livre'
        ).count()

        annulees = commandes.filter(
        statut='annule'
        ).count()

        chiffre_affaires = commandes.aggregate(

            total=Sum("montant_total")

        )["total"] or 0

        return Response({

        "total_commandes": total,

        "en_attente": en_attente,

        "confirmees": confirmees,

        "expediees": expediees,

        "livrees": livrees,

        "annulees": annulees,

        "chiffre_affaires": chiffre_affaires

    })