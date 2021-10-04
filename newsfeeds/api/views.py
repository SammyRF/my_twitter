from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.decorators import rate_limit
from utils.paginations import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_queryset(self):
        return NewsFeed.objects.filter(user_id=self.request.user.id)

    @rate_limit(hms=(0, 6, 0))
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
