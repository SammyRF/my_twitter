from rest_framework import serializers
from accounts.api.serializers import UserShortSerializer
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetShortSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    tweet = TweetShortSerializer()

    class Meta:
        model = NewsFeed
        fields = ('created_at', 'user', 'tweet')