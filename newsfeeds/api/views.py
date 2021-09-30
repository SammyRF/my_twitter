from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        # DB direct
        # newsfeeds = NewsFeed.objects.filter(user=request.user).order_by('-created_at')

        # Redis cache
        newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        newsfeeds = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(
            newsfeeds,
            context={'user': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
