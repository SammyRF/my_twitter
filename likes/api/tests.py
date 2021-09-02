from django.test import TestCase
from utils.test_helpers import TestHelpers
from rest_framework.test import APIClient
from rest_framework import status

BASE_LIKE_URL = '/api/likes/'


class LikeApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()

        self.admin = TestHelpers.create_user()
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin)
        self.user1 = TestHelpers.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.tweet = TestHelpers.create_tweet(self.admin)
        self.comment = TestHelpers.create_comment(self.user1, self.tweet)

    def test_tweets_likes(self):
        # ANONYMOUS is not allow to like
        response = self.anonymous_client.post(
            path=BASE_LIKE_URL,
            data = {'content_type': 'tweet', 'object_id': self.tweet.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'get' is not allowed
        response = self.user1_client.get(
            path=BASE_LIKE_URL,
            data={'content_type': 'tweet', 'object_id': self.tweet.id},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # normal case
        response = self.user1_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'tweet', 'object_id': self.tweet.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.tweet.like_set.count(), 1)

        # duplicated like will be ignored
        response = self.user1_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'tweet', 'object_id': self.tweet.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.tweet.like_set.count(), 1)

        # different likes
        response = self.admin_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'tweet', 'object_id': self.tweet.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_comments_likes(self):
        # ANONYMOUS is not allow to like
        response = self.anonymous_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'comment', 'object_id': self.comment.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'get' is not allowed
        response = self.user1_client.get(
            path=BASE_LIKE_URL,
            data={'content_type': 'comment', 'object_id': self.comment.id},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # normal case
        response = self.user1_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'comment', 'object_id': self.comment.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.comment.like_set.count(), 1)

        # duplicated like will be ignored
        response = self.user1_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'comment', 'object_id': self.comment.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.comment.like_set.count(), 1)

        # different likes
        response = self.admin_client.post(
            path=BASE_LIKE_URL,
            data={'content_type': 'comment', 'object_id': self.comment.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.comment.like_set.count(), 2)