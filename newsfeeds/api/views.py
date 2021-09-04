from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        serializer = NewsFeedSerializer(
            NewsFeed.objects.filter(user=self.request.user),
            context={'user': request.user},
            many=True,
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)
