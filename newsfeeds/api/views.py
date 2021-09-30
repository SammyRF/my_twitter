from newsfeeds.api.serializers import NewsFeedSerializer
from rest_framework import viewsets
from newsfeeds.models import NewsFeed
from rest_framework.permissions import IsAuthenticated
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(request, cached_newsfeeds)
        if page is None:
            queryset = NewsFeed.objects.filter(user=request.user).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context={'user': request.user},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
