from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from utils.test_helpers import TestHelpers

BASE_FRIENDSHIPS_URL = '/api/friendships/{}'
LIST_NO_PARAMS = BASE_FRIENDSHIPS_URL.format('')
LIST_FROM_USER_URL = BASE_FRIENDSHIPS_URL.format('?from_user_id=')
LIST_TO_USER_URL = BASE_FRIENDSHIPS_URL.format('?to_user_id=')
FOLLOW_URL = BASE_FRIENDSHIPS_URL.format('follow/')
UNFOLLOW_URL = BASE_FRIENDSHIPS_URL.format('unfollow/')


class FriendshipsApiTests(TestCase):

    def setUp(self):
        self.user1 = TestHelpers.create_user()
        self.user2 = TestHelpers.create_user(username='Staff', password='Staff', email='staff@staff.com')
        self.user3 = TestHelpers.create_user(username='Guest', password='Guest', email='guest@guest.com')

        TestHelpers.create_friendship(self.user1, self.user2)
        TestHelpers.create_friendship(self.user1, self.user3)
        TestHelpers.create_friendship(self.user2, self.user1)

        self.anonymous_client = APIClient()
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.user3_client = APIClient()
        self.user3_client.force_authenticate(self.user3)

    def test_list_api(self):
        # no params are not allowed
        response = self.anonymous_client.get(LIST_NO_PARAMS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # wrong user id return empty list
        response = self.anonymous_client.get(LIST_FROM_USER_URL + '1000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['friendships']), 0)

        # POST not allowed
        response = self.anonymous_client.post(LIST_FROM_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # user1 follows 2 users
        response = self.anonymous_client.get(LIST_FROM_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['friendships']), 2)

        #user1 followed by 1 user
        response = self.anonymous_client.get(LIST_TO_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['friendships']), 1)

    def test_follow_api(self):
        # GET not allowed
        response = self.user1_client.get(FOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # authenticate is needed
        response = self.anonymous_client.post(FOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # user cannot follow himself
        response = self.user1_client.post(FOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # normal follow case
        response = self.user3_client.post(FOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # follow same user again
        response = self.user3_client.post(FOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'friendship exists')

    def test_unfollow_api(self):
        # GET not allowed
        response = self.user1_client.get(UNFOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # authenticate is needed
        response = self.anonymous_client.post(UNFOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # user cannot unfollow himself
        response = self.user1_client.post(UNFOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'user cannot unfollow himself')

        # normal unfollow case
        response = self.user2_client.post(UNFOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'friendship deleted')

        # unfollow same user again
        response = self.user2_client.post(UNFOLLOW_URL, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'friendship not found')



