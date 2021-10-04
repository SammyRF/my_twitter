from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from utils.caches.redis_helper import RedisHelper, USER_NEWSFEEDS_PATTERN
from newsfeeds.tasks import fan_out_main_task




class NewsFeedService:

    @classmethod
    def fan_out(cls, tweet):
        fan_out_main_task.delay(tweet.id, tweet.user_id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.get_objects_from_redis(key, queryset)

    @classmethod
    def extend_cached_newsfeed(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.extend_object_in_redis(key, newsfeed, queryset)