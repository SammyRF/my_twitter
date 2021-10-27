from celery import shared_task
from django.conf import settings
from friendships.models import Friendship
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

FANOUT_TIME_LIMIT = 3600 # 1hour
FANOUT_BATCH_SIZE = 1000 if not settings.TESTING else 3


@shared_task(routing_key='default', time_limit=FANOUT_TIME_LIMIT)
def fan_out_main_task(tweet_id, tweet_user_id):
    # add user self first, make sure that user can see it in his own newsfeed fast
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    friendships = FriendshipService.get_friendships(to_user_id=tweet_user_id)
    from_user_ids = [friendship.from_user_id for friendship in friendships]
    idx = 0
    while idx < len(from_user_ids):
        batch_ids = from_user_ids[idx : idx + FANOUT_BATCH_SIZE]
        fan_out_batch_task.delay(tweet_id, batch_ids)
        idx += FANOUT_BATCH_SIZE

    size = len(from_user_ids)
    return f'{size} newsfeeds fan out with {(size - 1) // FANOUT_BATCH_SIZE + 1} batches.'


@shared_task(routing_key='newsfeeds', time_limit=FANOUT_TIME_LIMIT)
def fan_out_batch_task(tweet_id, from_user_ids):
    from newsfeeds.services import NewsFeedService

    newsfeeds = [NewsFeed(user_id=from_user_id, tweet_id=tweet_id) for from_user_id in from_user_ids]

    # bulk_create improved performance
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk_create will not trigger post_save, need to put to redis manually
    for newsfeed in newsfeeds:
        NewsFeedService.extend_newsfeed_in_redis(newsfeed)

    return f'{len(newsfeeds)} newsfeeds are created.'


