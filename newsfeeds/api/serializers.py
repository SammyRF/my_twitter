from accounts.api.serializers import UserShortSerializer
from newsfeeds.models import NewsFeed
from rest_framework import serializers
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ('created_at', 'user', 'tweet')
