from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import ProfilSerializer, ModifierProfilSerializer, ChangerMotDePasseSerializer

Utilisateur = get_user_model()

class ProfilViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilSerializer

    @action(detail=False, methods=['get'])
    def mon_profil(self, request):
        serializer = ProfilSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def modifier(self, request):
        serializer = ModifierProfilSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(ProfilSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def changer_mot_de_passe(self, request):
        serializer = ChangerMotDePasseSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['nouveau_mot_de_passe'])
            request.user.save()
            return Response({'message': 'Mot de passe changé avec succès'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)