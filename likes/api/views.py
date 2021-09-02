from likes.api.serializers import LikeSerializerForCreate, LikeSerializer
from likes.models import Like
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.decorators import required_all_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializerForCreate
    permission_classes = [IsAuthenticated]

    @required_all_params(params_src='data', params=('content_type', 'object_id'))
    def create(self, request):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'user': request.user},
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        like = serializer.save()
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)
