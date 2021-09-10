from accounts.api.serializers import UserSerializerWithProfile
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeServices
from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerWithProfile()
    has_like = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'created_at',
            'user',
            'content',
            'has_like',
            'like_count',
            'comment_count',
            'likes',
            'comments',
        )

    def get_has_like(self, obj):
        return LikeServices.has_like(self.context['user'], obj)

    def get_like_count(self, obj):
        return obj.like_set.count()

    def get_comment_count(self, obj):
        return obj.comment_set.count()


class TweetSerializerForCreate(serializers.Serializer):
    content = serializers.CharField(min_length=5, max_length=120)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        return Tweet.objects.create(user=user, content=content)

