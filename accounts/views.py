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
from .serializers import EarlyAccessUserSerializer, ProfileSerializer, SignupSerializer, LoginSerializer
from .models import Profile

class SignupView(generics.CreateAPIView):
  permission_classes = (AllowAny,)
  serializer_class = SignupSerializer

class ProfileView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        profile, create = Profile.objects.get_or_create(user=user)
        profile.phoneNumber = serializer.data.get('phoneNumber')
        profile.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        user = request.user
        profile, create = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(user, context={'profile': profile})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def signinView(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user.save()

        return Response(
            {
                'token': token.key,
                'email': user.email,
            },
            status=status.HTTP_200_OK
        )
    else:
        print(serializer.errors)
        try:
            message = serializer.errors['non_field_errors'][0]
        except (IndexError, KeyError) as e:
            message = "Some random message I don't know y"

    return Response({'message': message}, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)

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
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)