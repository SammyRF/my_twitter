from django.test import TestCase
from utils.test_helpers import TestHelpers
from rest_framework.test import APIClient
from rest_framework import status

BASE_LIKE_URL = '/api/likes/'
CANCEL_LIKE_URL = '/api/likes/cancel/'


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

    def test_cancel(self):
        like_comment_data = {'content_type': 'comment', 'object_id': self.comment.id}
        like_tweet_data = {'content_type': 'tweet', 'object_id': self.tweet.id}
        self.admin_client.post(BASE_LIKE_URL, like_comment_data)
        self.user1_client.post(BASE_LIKE_URL, like_tweet_data)
        self.assertEqual(self.tweet.like_set.count(), 1)
        self.assertEqual(self.comment.like_set.count(), 1)

        # ANONYMOUS is not allowed
        response = self.anonymous_client.post(CANCEL_LIKE_URL, like_comment_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.anonymous_client.post(CANCEL_LIKE_URL, like_tweet_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'Get' not allowed
        response = self.user1_client.get(CANCEL_LIKE_URL, like_comment_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.admin_client.get(CANCEL_LIKE_URL, like_tweet_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # other user not allowed
        response = self.user1_client.post(CANCEL_LIKE_URL, like_comment_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.admin_client.post(CANCEL_LIKE_URL, like_tweet_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # normal case
        response = self.admin_client.post(CANCEL_LIKE_URL, like_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.comment.like_set.count(), 0)
        response = self.user1_client.post(CANCEL_LIKE_URL, like_tweet_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.tweet.like_set.count(), 0)

