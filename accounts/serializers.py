import shutil
import os
import hashlib
import datetime
import pandas as pd
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import EarlyAccessUser, Profile
from mainapp.models import TradeHistory, Portfolio, PortfolioEntry
from django.conf import settings


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

        #default portfolio
        portfolio = Portfolio(
            user=user, 
            name='My portfolio'
        )
        portfolio_entry = PortfolioEntry(
            portfolio = portfolio, 
            type=0, 
            value=0, 
            desc='This is a test deposit', 
            date=datetime.datetime.now()
        )
        
        #demo trades
        demo_filename = hashlib.md5(('demo:'+user.username).encode()).hexdigest()+'.csv'
        demo_merged_filename = os.path.join(settings.MERGED_TRADES_PATH, demo_filename)
        demo_output_filename = os.path.join(settings.OUTPUT_TRADES_PATH, demo_filename)

        demo_trade_history = TradeHistory(
            user=user, 
            merged_trades = demo_merged_filename, 
            output_trades = demo_output_filename, 
            is_demo = True)
        user.set_password(validated_data['password'])
        shutil.copy(settings.DEMO_MERGED_TRADES_PATH, demo_merged_filename)
        shutil.copy(settings.DEMO_OUTPUT_TRADES_PATH, demo_output_filename)
        portfolio.save()
        portfolio_entry.save()
        demo_trade_history.save()
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
    class Meta:
        model = Profile
        fields = ('phoneNumber', 'picture')

class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    profile = ProfileSerializer(read_only = False)

    class Meta:
        model = User
        fields = ('firstName', 'lastName', 'email', 'username', 'profile')
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
            }
        }

    def update(self, instance, validated_data): 
        profile_data = validated_data.pop('profile')
        profile = Profile.objects.filter(user = instance)
        profile.update(**profile_data)
        super().update(instance=instance, validated_data=validated_data)
        return instance

class ProfilePictureSerializer(serializers.Serializer):
    class Meta:
        model = Profile
        fields = ('picture')

class ChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])
    rePassword = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('rePassword'):
            raise serializers.ValidationError({"rePassword": "Password fields didn't match."})
        return attrs
