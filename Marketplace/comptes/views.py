# Create your views here.
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import ProfilSerializer, ModifierProfilSerializer, ChangerMotDePasseSerializer

User = get_user_model()
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import JsonResponse

from .serializers import RegisterSerializer, UserSerializer


def test_account(_request):
    assert _request is not None
    return JsonResponse({"message": "Accounts OK"})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')

        if username and '@' in username:
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass

        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfilViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

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