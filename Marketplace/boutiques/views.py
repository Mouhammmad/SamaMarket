from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView
)

from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser
)

from produits.models import (
    Avis,
    Produit,
    Promotion
)

from produits.serializers import (
    AvisSerializer,
    ProduitSerializer
)

from .models import Boutique

from .serializers import (
    BoutiqueSerializer,
    BoutiqueCreateSerializer
)
from rest_framework import status
from comptes.models import SuiviBoutique


# ==============================================================
# MA BOUTIQUE
# ==============================================================

class MaBoutiqueView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser
    ]

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------

    def get(self, request):

        try:

            boutique = Boutique.objects.get(
                responsable=request.user
            )

        except Boutique.DoesNotExist:

            return Response(
                {
                    "detail": "Aucune boutique"
                },
                status=404
            )

        serializer = BoutiqueSerializer(
            boutique,
            context={
                'request': request
            }
        )

        return Response(
            serializer.data
        )

    # ----------------------------------------------------------
    # PUT
    # ----------------------------------------------------------

    def put(self, request):

        try:

            boutique = Boutique.objects.get(
                responsable=request.user
            )

        except Boutique.DoesNotExist:

            return Response(
                {
                    "detail": "Aucune boutique"
                },
                status=404
            )

        serializer = BoutiqueSerializer(
            boutique,
            data=request.data,
            partial=True,
            context={
                'request': request
            }
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                BoutiqueSerializer(
                    serializer.instance,
                    context={
                        'request': request
                    }
                ).data
            )

        return Response(
            serializer.errors,
            status=400
        )

    # ----------------------------------------------------------
    # PATCH
    # ----------------------------------------------------------

    def patch(self, request):

        return self.put(request)
class ParametresBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            boutique = Boutique.objects.get(
                responsable=request.user
            )
        except Boutique.DoesNotExist:
            return Response(
                {"detail": "Aucune boutique"},
                status=404
            )

        serializer = BoutiqueSerializer(
            boutique,
            context={'request': request}
        )

        return Response(serializer.data)

    def put(self, request):
        try:
            boutique = Boutique.objects.get(
                responsable=request.user
            )
        except Boutique.DoesNotExist:
            return Response(
                {"detail": "Aucune boutique"},
                status=404
            )

        champs_autorises = [
            'nom',
            'description',
            'ville',

            'telephone',
            'email',
            'whatsapp',

            'zones_livraison',
            'delai_livraison',
            'frais_livraison',

            'retours_acceptes',
            'delai_retour',

            'wave_actif',
            'orange_money_actif',

            'notifications_commandes',
            'notifications_avis',
            'notifications_messages',
        ]

        for champ in champs_autorises:

            if champ in request.data:
                setattr(
                    boutique,
                    champ,
                    request.data[champ]
                )

        boutique.save()

        serializer = BoutiqueSerializer(
            boutique,
            context={'request': request}
        )

        return Response(serializer.data)

# ==============================================================
# LISTE DES BOUTIQUES
# ==============================================================

class VueListeBoutiques(ListAPIView):

    queryset = Boutique.objects.all()

    serializer_class = BoutiqueSerializer

    permission_classes = [
        AllowAny
    ]


# ==============================================================
# DETAIL D'UNE BOUTIQUE
# ==============================================================

class VueDetailBoutique(RetrieveAPIView):

    queryset = Boutique.objects.all()

    serializer_class = BoutiqueSerializer

    permission_classes = [
        AllowAny
    ]

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['request'] = self.request

        return context


# ==============================================================
# PRODUITS D'UNE BOUTIQUE
# ==============================================================

class VueProduitsDeLaBoutique(ListAPIView):

    serializer_class = ProduitSerializer

    permission_classes = [
        AllowAny
    ]

    def get_queryset(self):

        return Produit.objects.filter(
            boutique_id=self.kwargs['pk']
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['request'] = self.request

        return context


# ==============================================================
# AVIS D'UNE BOUTIQUE
# ==============================================================

class VueAvisDeLaBoutique(ListAPIView):

    serializer_class = AvisSerializer

    permission_classes = [
        AllowAny
    ]

    def get_queryset(self):

        return Avis.objects.filter(
            produit__boutique_id=self.kwargs['pk'],
            est_approuve=True
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['request'] = self.request

        return context


# ==============================================================
# PROMOTIONS D'UNE BOUTIQUE
# ==============================================================

class VuePromotionsDeLaBoutique(ListAPIView):

    permission_classes = [
        AllowAny
    ]

    def get_queryset(self):

        return Promotion.objects.filter(
            boutique_id=self.kwargs['pk'],
            est_active=True
        )

    def get(self, request, *args, **kwargs):

        promotions = self.get_queryset()

        data = []

        for promotion in promotions:

            data.append({

                'id': promotion.id,

                'code': promotion.code,

                'taux_remise': promotion.taux_remise,

                'type_remise': promotion.type_remise,

                'date_debut': promotion.date_debut,

                'date_fin': promotion.date_fin,

                'est_active': promotion.est_active,

                'limite_usage': promotion.limite_usage,

                'nombre_utilise': promotion.nombre_utilise,

                'produits': list(
                    promotion.produits.values(
                        'id',
                        'nom',
                        'prix'
                    )
                )

            })

        return Response(
            data
        )


# ==============================================================
# CREER UNE BOUTIQUE
# ==============================================================

class VueCreerBoutique(CreateAPIView):

    serializer_class = BoutiqueCreateSerializer

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser
    ]

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context["request"] = self.request

        return context

    def perform_create(self, serializer):

        serializer.save()

class SuivreBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            boutique = Boutique.objects.get(pk=pk)
        except Boutique.DoesNotExist:
            return Response(
                {"detail": "Boutique introuvable."},
                status=404
            )

        suivi, created = SuiviBoutique.objects.get_or_create(
            utilisateur=request.user,
            boutique=boutique
        )

        if created:
            boutique.followers += 1
            boutique.save(update_fields=['followers'])

            message = "Boutique suivie avec succès."
        else:
            message = "Vous suivez déjà cette boutique."

        return Response({
            "suivi": True,
            "followers": boutique.followers,
            "message": message
        })


    def delete(self, request, pk):

        try:
            boutique = Boutique.objects.get(pk=pk)
        except Boutique.DoesNotExist:
            return Response(
                {"detail": "Boutique introuvable."},
                status=404
            )

        suivi = SuiviBoutique.objects.filter(
            utilisateur=request.user,
            boutique=boutique
        ).first()

        if suivi:

            suivi.delete()

            if boutique.followers > 0:
                boutique.followers -= 1
                boutique.save(update_fields=['followers'])

            message = "Vous ne suivez plus cette boutique."

        else:
            message = "Vous ne suiviez pas cette boutique."

        return Response({
            "suivi": False,
            "followers": boutique.followers,
            "message": message
        })


class StatutSuiviBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            boutique = Boutique.objects.get(pk=pk)
        except Boutique.DoesNotExist:
            return Response(
                {"detail": "Boutique introuvable."},
                status=404
            )

        suivi = SuiviBoutique.objects.filter(
            utilisateur=request.user,
            boutique=boutique
        ).exists()

        return Response({
            "suivi": suivi,
            "followers": boutique.followers
        })