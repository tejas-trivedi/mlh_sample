from django.contrib.auth import authenticate, user_logged_in, user_login_failed
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import Role, User, ACMMEMBER, GuestUser



class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email_id', 'password')

    def validate(self, attrs):
        # print(attrs)
        user = authenticate(
            email_id=attrs['email_id'], password=attrs['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            print(token.key)
            return token.key
        else:
            token = ''
            return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email_id', 'roles', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email_id=validated_data['email_id'], roles=validated_data['roles'][0], password=validated_data['password'])
        user.save()
        return user


class GuestSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestUser
        fields = ['guest_name', 'guest_email']
        
        

