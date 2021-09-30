from django.test import TestCase
from tweets.models import TweetPhoto
from utils.caches.redis_client import RedisClient
from utils.caches.redis_serializers import DjangoModelSerializer
from utils.test_helpers import TestHelpers


class TweetPhotoTests(TestCase):
    def setUp(self):
        TestHelpers.clear_cache()
        
        self.admin = TestHelpers.create_user()
        self.tweet = TestHelpers.create_tweet(self.admin)

    def test_tweetphoto(self):
        tweet_photo = TweetPhoto.objects.create(
            user=self.admin,
            tweet=self.tweet,
        )
        self.assertEqual(tweet_photo.user, self.admin)
        self.assertEqual(tweet_photo.tweet, self.tweet)
        self.assertEqual(TweetPhoto.objects.all().count(), 1)

    def test_cache_tweet_in_redis(self):
        conn = RedisClient.get_connection()
        serializerd_data = DjangoModelSerializer.serialize(self.tweet)
        conn.set(f'tweet:{self.tweet.id}', serializerd_data)
        data = conn.get(f'nothing')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{self.tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(self.tweet, cached_tweet)


