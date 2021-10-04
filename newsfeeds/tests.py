from django.test import TestCase
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fan_out_main_task
from rest_framework.test import APIClient
from utils.test_helpers import TestHelpers


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        TestHelpers.clear_cache()
        self.user1 = TestHelpers.create_user()
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

    def test_get_cached_newsfeeds(self):
        # no newsfeed
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(newsfeeds, [])

        # post tweets
        self.user1_client.post('/api/tweets/', {'content': 'tweet1'})
        self.user1_client.post('/api/tweets/', {'content': 'tweet2'})

        # redis miss and load
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        newsfeeds = [newsfeed.tweet.content for newsfeed in newsfeeds]
        self.assertEqual(newsfeeds, ['tweet2', 'tweet1'])

        # redis hit
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        newsfeeds = [newsfeed.tweet.content for newsfeed in newsfeeds]
        self.assertEqual(newsfeeds, ['tweet2', 'tweet1'])

        # extend newsfeed
        self.user1_client.post('/api/tweets/', {'content': 'tweet3'})
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        newsfeeds = [newsfeed.tweet.content for newsfeed in newsfeeds]
        self.assertEqual(newsfeeds, ['tweet3', 'tweet2', 'tweet1'])


class NewsFeedTaskTests(TestCase):
    def setUp(self):
        TestHelpers.clear_cache()
        self.admin = TestHelpers.create_user()

    def test_fan_out_main_task(self):
        for i in range(1, 5):
            user = TestHelpers.create_user(username=f'user{i}')
            TestHelpers.create_friendship(user, self.admin)
        tweet = TestHelpers.create_tweet(self.admin)
        msg = fan_out_main_task(tweet.id, tweet.user_id)
        self.assertEqual(msg, '4 newsfeeds fan out with 2 batches.')
