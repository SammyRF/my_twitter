from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer, SignupSerializer, LoginSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer
    permission_classes = (AllowAny, )

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # check input
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'error': serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # authenticate
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'username and password does not match',
            }, status=400)

        # login
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(instance=user).data
        })

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({
            'success': True,
        })

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        return Response({
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # check input
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'error': serializer.errors,
            }, status=400)

        # create user
        user = serializer.save()

        # auto login
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(instance=user).data
        }, status=201)

    @action(methods=['POST'], detail=False)
    def signoff(self, request):
        # check input
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'error': serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # not allow delete 'admin'
        if username == 'admin':
            return Response({
                'success': False,
                'message': 'admin cannot be signed off'
            }, status=403)

        # authenticate
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'username and password does not match',
            }, status=400)

        # logout
        if request.user == user:
            django_logout(request)

        # signoff
        User.objects.filter(username=username).delete()
        return Response({
            'success': True,
            'user': UserSerializer(instance=user).data
        })
