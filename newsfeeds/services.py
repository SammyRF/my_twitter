from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from utils.caches.redis_helper import RedisHelper, USER_NEWSFEEDS_PATTERN


def fan_out(user, tweet):
    # prefetch improved performance
    friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
    newsfeeds = [NewsFeed(user=friendship.from_user, tweet=tweet) for friendship in friendships]

    # add user self
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))

    # bulk_create improved performance
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk_create will not trigger post_save, need to put to redis manually
    for newsfeed in newsfeeds:
        NewsFeedService.extend_cached_newsfeed(newsfeed)


class NewsFeedService:

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