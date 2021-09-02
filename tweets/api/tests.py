from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from tweets.models import Tweet
from utils.test_helpers import TestHelpers
from utils.time_helpers import TimeHelpers

BASE_TWEETS_URL = '/api/tweets/{}'
TWEET_LIST_URL = BASE_TWEETS_URL.format('')
TWEET_CREATE_URL = BASE_TWEETS_URL.format('')
TWEET_RETRIEVE_URL = BASE_TWEETS_URL + '/'

class TweetTests(TestCase):

    def setUp(self):
        self.user1 = TestHelpers.create_user()
        self.user1.tweets = [TestHelpers.create_tweet(self.user1) for _ in range(2)]
        self.user2 = TestHelpers.create_user(username='Guest', password='Guest', email='guest@guest.com')
        self.user2.tweets = [TestHelpers.create_tweet(self.user2) for _ in range(3)]
        self.anonymous_client = APIClient()
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

    def test_hours_to_now(self):
        user1 = User.objects.create_user(username='user1')
        tweet = Tweet.objects.create(user=user1, content="")
        tweet.created_at = TimeHelpers.utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_list_api(self):
        # check used_it is mandatory
        response = self.anonymous_client.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, 400)

        # check normal case
        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 2)
        self.assertEqual(response.data['tweets'][0]['id'], self.user1.tweets[-1].id)
        self.assertEqual(response.data['tweets'][-1]['id'], self.user1.tweets[0].id)

    def test_create_api(self):
        # test anonymous forbidden
        response = self.anonymous_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # no content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # content size less than 5
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': 'a'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # content size more than 120
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': 'a' * 121})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # normal case
        tweet_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': 'test content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweet_count + 1)

    def test_retrieve_api(self):
        # tweet with minus value not exists
        url = TWEET_RETRIEVE_URL.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # tweet with comment
        tweet = TestHelpers.create_tweet(self.user1)
        url = TWEET_RETRIEVE_URL.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        comment = TestHelpers.create_comment(self.user2, tweet)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 1)
