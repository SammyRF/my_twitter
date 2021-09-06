from django.test import TestCase
from inbox.services import NotificationSerivce
from utils.test_helpers import TestHelpers
from rest_framework.test import APIClient
from notifications.models import Notification


class NotificationsServiceTests(TestCase):

    def setUp(self):
        self.admin = TestHelpers.create_user()
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin)

        self.user1 = TestHelpers.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

    def test_notify_like(self):
        tweet = TestHelpers.create_tweet(self.admin)
        comment = TestHelpers.create_comment(self.admin, tweet)

        # no notification when like self tweet
        like = TestHelpers.create_like(self.admin, tweet)
        NotificationSerivce.send_like_notification(like)
        self.assertEqual(Notification.objects.all().count(), 0)

        # no notification when like self comment
        like = TestHelpers.create_like(self.admin, comment)
        NotificationSerivce.send_like_notification(like)
        self.assertEqual(Notification.objects.all().count(), 0)

        # notify when someone like your tweet
        like = TestHelpers.create_like(self.user1, tweet)
        NotificationSerivce.send_like_notification(like)
        self.assertEqual(Notification.objects.all().count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 0)
        self.assertEqual(Notification.objects.filter(recipient=self.admin).count(), 1)

        # notify when someone like your tweet
        like = TestHelpers.create_like(self.user1, comment)
        NotificationSerivce.send_like_notification(like)
        self.assertEqual(Notification.objects.all().count(), 2)
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 0)
        self.assertEqual(Notification.objects.filter(recipient=self.admin).count(), 2)

    def test_notify_comment(self):
        tweet = TestHelpers.create_tweet(self.admin)

        # no notification when comments self tweet
        comment = TestHelpers.create_comment(self.admin, tweet)
        NotificationSerivce.send_comment_notification(comment)
        self.assertEqual(Notification.objects.all().count(), 0)

        # notify when someone comments your tweet
        comment = TestHelpers.create_comment(self.user1, tweet)
        NotificationSerivce.send_comment_notification(comment)
        self.assertEqual(Notification.objects.all().count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 0)
        self.assertEqual(Notification.objects.filter(recipient=self.admin).count(), 1)
