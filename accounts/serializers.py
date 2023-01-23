from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import EarlyAccessUser, Profile

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all(), 
        message="A user with this email already exist.")])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    rePassword = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'rePassword', 'email')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('rePassword'):
            raise serializers.ValidationError({"rePassword": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'], email=validated_data['email'])
        Profile.objects.create(user = user)
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                msg = _("Unable to Login with the credentials provided")
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _("Must include email and password.")
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class EarlyAccessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarlyAccessUser
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    # phoneNumber = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('firstName', 'lastName', 'email', 'username')
        # , 'phoneNumber')
        extra_kwargs = {
            'firstName': {
                'required': True
            },
            'lastName': {
                'required': True
            },
            'email': {
                'read_only': True
            },
            'username': {
                'read_only': True
            },
            # 'phoneNumber': {
            #     'required': True
            # }
        }

    # def get_phoneNumber(self, user):
    #     profile = self.context.get('profile')
    #     if(profile):
    #         return profile.phoneNumber
    #     return 