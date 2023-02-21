from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from .serializers import EarlyAccessUserSerializer, UserSerializer, SignupSerializer, LoginSerializer, ProfilePictureSerializer, ChangePasswordSerializer, PortfolioSeriliser
from .models import Profile, Portfolio

class SignupView(generics.CreateAPIView):
  permission_classes = (AllowAny,)
  serializer_class = SignupSerializer

class UserView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfilePictureView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer = ProfilePictureSerializer

    def put(self, request):
        user = request.user
        serializer = self.serializer(user, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        serializer = self.serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def change_password_view(request):
    user = request.user
    change_password_serializer = ChangePasswordSerializer(data = request.data)
    if change_password_serializer.is_valid():
        data = change_password_serializer.data
        if user.check_password(data['oldPassword']):
            user.set_password(data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'oldPassword': 'Invalied password'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(change_password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signinView(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.save()
        return Response({'token': token.key, 'email': user.email}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def signoutView(request):
    request.user.auth_token.delete()
    logout(request)
    return Response({"message": "User Logged out successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def earlyAccessUserView(request):
    serializer = EarlyAccessUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfoliosView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer = PortfolioSeriliser

    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        portfolios = Portfolio.objects.filter(user = request.user)
        if portfolios.exists():
            serializer = self.serializer(portfolios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request):
        portfolios = Portfolio.objects.filter(user = request.user, pk = request.data['pk'])
        if portfolios.exists():
            portfolios.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    