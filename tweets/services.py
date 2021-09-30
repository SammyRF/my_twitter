from tweets.models import Tweet
from utils.caches.redis_helper import RedisHelper, USER_TWEETS_PATTERN


class TweetService:

    @classmethod
    def get_cached_tweets(cls, user_id):
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=user_id)
        return RedisHelper.get_objects_from_redis(key, queryset)

    @classmethod
    def extend_cached_tweet(cls, tweet):
        queryset = Tweet.objects.filter(user_id=tweet.user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.extend_object_in_redis(key, tweet, queryset)