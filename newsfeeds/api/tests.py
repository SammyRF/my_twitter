from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from utils.test_helpers import TestHelpers

NEWSFEEDS_URL = '/api/newsfeeds/'
TWEET_CREATE_URL = '/api/tweets/'

class NewsFeedApiTests(TestCase):
    def setUp(self):
        self.user1 = TestHelpers.create_user()
        self.user2 = TestHelpers.create_user(username='Staff', password='Staff', email='staff@staff.com')

        TestHelpers.create_friendship(self.user1, self.user2)
        TestHelpers.create_friendship(self.user2, self.user1)

        self.anonymous_client = APIClient()
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list_api(self):
        # anonymous is not allowed
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # POST is not allowed
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # newsfeeds count is 0 by default
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # newsfeed count of user1 is 1 after user1 post tweet
        self.user1_client.post(TWEET_CREATE_URL, {'content': 'test content'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # newsfeed count of user1 is 2 after user2 post tweet, because user1 follow user2
        self.user2_client.post(TWEET_CREATE_URL, {'content': 'test content'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 2)
