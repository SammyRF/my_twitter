from django.test import TestCase
from notifications.models import Notification
from rest_framework import status
from rest_framework.test import APIClient
from utils.test_helpers import TestHelpers

CREATE_LIKE_URL = '/api/likes/'
CREATE_COMMENT_URL = '/api/comments/'


class NotificationsServiceTests(TestCase):

    def setUp(self):
        self.admin = TestHelpers.create_user()
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin)

        self.user1 = TestHelpers.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

    def test_notify_like_api(self):
        tweet = TestHelpers.create_tweet(self.admin)
        comment = TestHelpers.create_comment(self.admin, tweet)

        # notify when someone likes your tweet
        response = self.user1_client.post(CREATE_LIKE_URL, {
            'content_type': 'tweet',
            'object_id': tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.all().count(), 1)

        # notify when someone likes your comment
        response = self.user1_client.post(CREATE_LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.all().count(), 2)

    def test_notify_comment_api(self):
        tweet = TestHelpers.create_tweet(self.admin)

        # notify when someone comments your tweet
        response = self.user1_client.post(CREATE_COMMENT_URL, {
            'tweet_id': tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.all().count(), 1)
