from django.test import TestCase
from tweets.models import TweetPhoto
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

