from rest_framework import serializers
from accounts.api.serializers import UserSerializer
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

class TweetCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=5, max_length=120)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        return Tweet.objects.create(user=user, content=content)