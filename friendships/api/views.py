from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from friendships.api.serializers import FriendshipSerializer, FriendshipForCreateSerializer
from rest_framework.response import Response
from friendships.models import Friendship
from django.contrib.auth.models import User

class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipForCreateSerializer

    def list(self, request):
        # help function
        no_id = lambda id: not User.objects.filter(id=id).exists()

        # check id valid
        from_user_id = request.query_params.get('from_user_id')
        to_user_id = request.query_params.get('to_user_id')
        if no_id(from_user_id) and no_id(to_user_id):
            return Response({
                'success': False,
                'message': 'User not exists',
            }, status=status.HTTP_400_BAD_REQUEST)

        if from_user_id and to_user_id:
            friendships = Friendship.objects.filter(from_user_id=from_user_id, to_user_id=to_user_id)
        elif from_user_id:
            friendships = Friendship.objects.filter(from_user_id=from_user_id)
        elif to_user_id:
            friendships = Friendship.objects.filter(to_user_id=to_user_id)

        serializer = FriendshipSerializer(friendships, many=True)
        return Response(
            {'friendships': serializer.data},
            status = status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def follow(self, request):
        to_user_id = request.query_params.get('user_id')

        # if friendship exists, skip
        if Friendship.objects.filter(from_user=request.user, to_user_id=to_user_id).exists():
            return Response({
                'success': True,
                'message': 'friendship exists',
            })

        serializer = FriendshipForCreateSerializer(data={
            'from_user_id': request.user.id,
            'to_user_id': to_user_id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        friendship = serializer.save()
        return Response({
            'friendships': FriendshipSerializer(friendship).data,
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def unfollow(self, request):
        to_user_id = request.query_params.get('user_id')
        Friendship.objects.filter(from_user_id=request.user.id, to_user_id=to_user_id).delete()
        return Response({
            'success': True,
            'message': 'friendship deleted'
        }, status=status.HTTP_200_OK)




