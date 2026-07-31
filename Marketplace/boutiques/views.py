from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.generics import RetrieveUpdateAPIView

from produits.models import Avis, Produit
from produits.serializers import AvisSerializer, ProduitSerializer
from .serializers import BoutiqueCreateSerializer

from .models import Boutique
from .serializers import BoutiqueSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Boutique
from .serializers import BoutiqueSerializer, BoutiqueCreateSerializer


class MaBoutiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            boutique = Boutique.objects.get(responsable=request.user)
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


class VueListeBoutiques(ListAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    permission_classes = [AllowAny]


class VueDetailBoutique(RetrieveAPIView):
    queryset = Boutique.objects.all()
    serializer_class = BoutiqueSerializer
    permission_classes = [AllowAny]


class VueProduitsDeLaBoutique(ListAPIView):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Produit.objects.filter(boutique_id=self.kwargs['pk'])


class VueAvisDeLaBoutique(ListAPIView):
    serializer_class = AvisSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Avis.objects.filter(produit__boutique_id=self.kwargs['pk'])


class VuePromotionsDeLaBoutique(APIView):
    def get(self, request, pk):
        return Response(list(Produit.objects.filter(boutique_id=pk).values('id', 'title', 'discount', 'start_date', 'end_date')))


class VueCreerBoutique(CreateAPIView):
    serializer_class = BoutiqueCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save()
