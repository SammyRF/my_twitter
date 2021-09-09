from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class UserSerializerForSignup(serializers.Serializer):
    username = serializers.CharField(max_length=20, min_length=5)
    password = serializers.CharField(max_length=20, min_length=5)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate(self, data):
        username = data['username'].lower()
        password = data['password']
        email = data['email'].lower()
        if User.objects.filter(username=username).exists() \
            or User.objects.filter(email=email).exists():
            raise ValidationError({
                'message': 'This email address has been occupied'
            })
        data['username'] = username
        data['password'] = password
        data['email'] = email
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        password = validated_data['password']
        email = validated_data['email'].lower()
        user = User.objects.create_user(username=username, password=password, email=email)
        user.profile
        return user


class UserSerializerForLogin(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
