from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from utils.test_helpers import TestHelpers
from friendships.api.paginations import FriendshipPagination
from friendships.models import Friendship

BASE_FRIENDSHIPS_URL = '/api/friendships/{}'
LIST_NO_PARAMS = BASE_FRIENDSHIPS_URL.format('')
LIST_FROM_USER_URL = BASE_FRIENDSHIPS_URL.format('?from_user_id=')
LIST_TO_USER_URL = BASE_FRIENDSHIPS_URL.format('?to_user_id=')
FOLLOW_URL = BASE_FRIENDSHIPS_URL.format('follow/')
UNFOLLOW_URL = BASE_FRIENDSHIPS_URL.format('unfollow/')


class FriendshipsApiTests(TestCase):

    def setUp(self):
        TestHelpers.clear_cache()

        self.user1 = TestHelpers.create_user()
        self.user2 = TestHelpers.create_user(username='Staff', password='Staff', email='staff@staff.com')
        self.user3 = TestHelpers.create_user(username='Guest', password='Guest', email='guest@guest.com')

        self.anonymous_client = APIClient()
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        self.user3_client = APIClient()
        self.user3_client.force_authenticate(self.user3)

    def test_list_api(self):
        TestHelpers.create_friendship(self.user1, self.user2)
        TestHelpers.create_friendship(self.user1, self.user3)
        TestHelpers.create_friendship(self.user2, self.user1)

        # wrong user id return empty list
        response = self.anonymous_client.get(LIST_FROM_USER_URL + '1000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # POST not allowed
        response = self.anonymous_client.post(LIST_FROM_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # user1 follows 2 users
        response = self.anonymous_client.get(LIST_FROM_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        #user1 followed by 1 user
        response = self.anonymous_client.get(LIST_TO_USER_URL + str(self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_follow_api(self):
        TestHelpers.create_friendship(self.user1, self.user2)
        TestHelpers.create_friendship(self.user1, self.user3)
        TestHelpers.create_friendship(self.user2, self.user1)

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
        TestHelpers.create_friendship(self.user1, self.user2)
        TestHelpers.create_friendship(self.user1, self.user3)
        TestHelpers.create_friendship(self.user2, self.user1)

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

    def test_friendship_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            follower = TestHelpers.create_user('friendship_{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user1)

        # no params return first page
        response = self.anonymous_client.get(LIST_NO_PARAMS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        for result in response.data['results']:
            self.assertEqual(result['followed_from_user'], False)
            self.assertEqual(result['followed_to_user'], False)


        page = BASE_FRIENDSHIPS_URL.format('?page=')
        # anonymous hasn't followed any users
        response = self.anonymous_client.get(page + '1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
        self.assertEqual(len(response.data['results']), page_size)
        for result in response.data['results']:
            self.assertEqual(result['followed_from_user'], False)
            self.assertEqual(result['followed_to_user'], False)

        response = self.anonymous_client.get(page + '2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)
        for result in response.data['results']:
            self.assertEqual(result['followed_from_user'], False)
            self.assertEqual(result['followed_to_user'], False)

        response = self.anonymous_client.get(page + '3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



