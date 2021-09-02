from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import newsfeeds.services
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerWithComments
from tweets.models import Tweet
from utils.decorators import required_all_params


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_all_params(params=('user_id',))
    def list(self, request):
        if not 'user_id' in request.query_params:
            return Response({'message': 'missing user_id'}, status=status.HTTP_400_BAD_REQUEST)

        tweets = Tweet.objects.filter(user_id=request.query_params['user_id']).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        response = Response({'tweets': serializer.data})
        return response

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        tweet = serializer.save()
        newsfeeds.services.fan_out(user=request.user, tweet=tweet)
        return Response(TweetSerializer(tweet).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        tweet = Tweet.objects.filter(id=pk).first()
        if tweet:
            return Response(TweetSerializerWithComments(tweet).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'tweet not exists',
            }, status=status.HTTP_404_NOT_FOUND)

