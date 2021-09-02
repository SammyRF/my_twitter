from rest_framework import serializers
from accounts.api.serializers import UserSerializer
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Tweet
        fields = ('id', 'created_at', 'user', 'content')

class TweetShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tweet
        fields = ('content',)

class TweetSerializerForCreate(serializers.Serializer):
    content = serializers.CharField(min_length=5, max_length=120)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        return Tweet.objects.create(user=user, content=content)

class TweetSerializerWithComments(serializers.ModelSerializer):
    user = UserSerializer()
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'comments', 'created_at', 'content')
