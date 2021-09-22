from friendships.api.serializers import FriendshipSerializer, FriendshipForCreateSerializer
from friendships.models import Friendship
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils import helpers
from utils.decorators import required_any_params, required_all_params
from friendships.api.paginations import FriendshipPagination
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipForCreateSerializer
    queryset = User.objects.all()
    pagination_class = FriendshipPagination

    def list(self, request):
        from_user_id = request.query_params.get('from_user_id')
        to_user_id = request.query_params.get('to_user_id')
        if from_user_id and to_user_id:
            friendships = Friendship.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id).order_by('-created_at')
        elif from_user_id:
            friendships = Friendship.objects.filter(from_user_id=from_user_id).order_by('-created_at')
        elif to_user_id:
            friendships = Friendship.objects.filter(to_user_id=to_user_id).order_by('-created_at')
        else:
            friendships = Friendship.objects.all().order_by('-created_at')

        page = self.paginate_queryset(friendships)
        serializer = FriendshipSerializer(page, context={'user': request.user}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated,])
    @required_all_params(method='POST', params=('user_id',))
    def follow(self, request):
        to_user_id = request.data.get('user_id')

        # if friendship exists, skip
        if Friendship.objects.filter(from_user=request.user, to_user_id=to_user_id).exists():
            return Response({
                'success': True,
                'message': 'friendship exists',
            }, status=status.HTTP_200_OK)

        serializer = FriendshipForCreateSerializer(data={
            'from_user_id': request.user.id,
            'to_user_id': to_user_id,
        })

        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

        friendship = serializer.save()
        return Response({
            'friendships': FriendshipSerializer(friendship, context={'user': request.user}).data,
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    @required_all_params(method='POST', params=('user_id',))
    def unfollow(self, request):
        to_user_id = request.data.get('user_id')
        if str(request.user.id) == to_user_id:
            return Response({
                'success': False,
                'message': 'user cannot unfollow himself',
            }, status=status.HTTP_400_BAD_REQUEST)

        if not Friendship.objects.filter(from_user=request.user, to_user_id=to_user_id).exists():
            return Response({
                'success': False,
                'message': 'friendship not found',
            }, status=status.HTTP_400_BAD_REQUEST)

        Friendship.objects.filter(from_user_id=request.user.id, to_user_id=to_user_id).delete()
        return Response({
            'success': True,
            'message': 'friendship deleted'
        }, status=status.HTTP_200_OK)




