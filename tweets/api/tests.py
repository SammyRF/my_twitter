from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.helper_functions import time_helpers
from datetime import timedelta

class TweetTests(TestCase):

    def test_hours_to_now(self):
        user1 = User.objects.create_user(username='user1')
        tweet = Tweet.objects.create(user=user1, content="")
        tweet.create_at = time_helpers.utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
