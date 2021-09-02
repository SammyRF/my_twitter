from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate
)
from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from comments.api.permissions import IsObjectOwner
from utils import decorators, helpers

class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerForCreate
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action in ('create',):
            return [IsAuthenticated()]
        elif self.action in ('destroy', 'update', 'retrieve'):
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def create(self, request, *arg, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return helpers.validation_errors_response(serializer.errors)

        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *arg, **kwargs):
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data={'content': request.data['content']},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    def destroy(self, request, *arg, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({
            'success': True,
            'message': 'Comment deleted'
        }, status=status.HTTP_200_OK)

    @decorators.required_all_params(params=('tweet_id',))
    def list(self, request, *arg, **kwargs):
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, pk):
        comment = Comment.objects.filter(id=pk).first()
        if comment:
            return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'comment not exists',
            }, status=status.HTTP_404_NOT_FOUND)
