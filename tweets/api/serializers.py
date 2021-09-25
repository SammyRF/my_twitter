from accounts.api.serializers import UserSerializerWithProfile
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeServices
from rest_framework import serializers
from tweets.models import Tweet, TweetPhoto


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerWithProfile(source='cached_user')
    has_liked = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'created_at',
            'user',
            'content',
            'has_liked',
            'like_count',
            'comment_count',
            'likes',
            'comments',
            'photo_urls',
        )

    def get_has_liked(self, obj):
        return LikeServices.has_liked(self.context['user'], obj)

    def get_like_count(self, obj):
        return obj.like_set.count()

    def get_comment_count(self, obj):
        return obj.comment_set.count()

    def get_photo_urls(self, obj):
        return [photo.file.url for photo in obj.tweetphoto_set.all().order_by('order')]


class TweetSerializerForCreate(serializers.Serializer):
    content = serializers.CharField(min_length=5, max_length=120)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False,
        max_length=9,
    )

    class Meta:
        model = Tweet
        fields = ('content', 'files')

    def create(self, validated_data):
        user = self.context['user']
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        if validated_data.get('files'):
            photos = [
                TweetPhoto(tweet=tweet, user=user, file=file, order=idx)
                for idx, file in enumerate(validated_data['files'])
            ]
            TweetPhoto.objects.bulk_create(photos)
        return tweet

