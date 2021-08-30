from django.test import TestCase
from utils.test_helpers import TestHelpers



class CommentsModelTests(TestCase):

    def test_comment(self):
        user = TestHelpers.create_user()
        tweet = TestHelpers.create_tweet(user)
        comment = TestHelpers.create_comment(user, tweet)
        self.assertNotEqual(comment, None)
