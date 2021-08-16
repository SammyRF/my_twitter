from tweets.models import Tweet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer

class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action in ('list', ):
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if not 'user_id' in request.query_params:
            return Response({'message': 'missing user_id'}, status=status.HTTP_400_BAD_REQUEST)

        tweets = Tweet.objects.filter(user_id=request.query_params['user_id']).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        response = Response({'tweets': serializer.data})
        return response

    def create(self, request, *args, **kwargs):
        serializer = TweetCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=status.HTTP_201_CREATED)
