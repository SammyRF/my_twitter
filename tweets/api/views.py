from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from tweets.services import TweetService
from utils import helpers
from utils.decorators import required_all_params
from utils.paginations import EndlessPagination
import newsfeeds.services



class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_all_params(method='GET', params=('user_id',))
    def list(self, request):
        # DB direct version
        # tweets = Tweet.objects.filter(user_id=request.query_params['user_id']).order_by('-created_at')

        # Redis version
        tweets = TweetService.get_cached_tweets(request.query_params['user_id'])
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(tweets, context={'user': request.user}, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

        tweet = serializer.save()
        newsfeeds.services.fan_out(user=request.user, tweet=tweet)
        return Response(TweetSerializer(tweet, context={'user': request.user}).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        tweet = Tweet.objects.filter(id=pk).first()
        if tweet:
            return Response(TweetSerializer(tweet, context={'user': request.user}).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'tweet not exists',
            }, status=status.HTTP_404_NOT_FOUND)

