from accounts.models import UserProfile
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    UserSerializerForSignup,
    UserSerializerForLogin,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate,
)
from utils import helpers
from utils.permissions import IsObjectOwner



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializerWithProfile
    permission_classes = (IsAdminUser,)


class AccountViewSet(viewsets.ViewSet):
    serializer_class = UserSerializerForSignup
    permission_classes = (AllowAny, )

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # check input
        serializer = UserSerializerForLogin(data=request.data)
        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

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
        serializer = UserSerializerForSignup(data=request.data)
        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

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
        serializer = UserSerializerForLogin(data=request.data)
        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

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


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate

