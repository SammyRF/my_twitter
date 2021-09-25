from django.test import TestCase
from friendships.models import Friendship
from friendships.services import FriendshipService
from utils.test_helpers import TestHelpers

class FriendshipServiceTests(TestCase):

    def setUp(self):
        TestHelpers.clear_cache()
        self.user1 = TestHelpers.create_user('user1')
        self.user2 = TestHelpers.create_user('user2')
        self.user3 = TestHelpers.create_user('user3')
        self.user4 = TestHelpers.create_user('user4')

    def test_get_to_users(self):
        for to_user in [self.user2, self.user3, self.user4]:
            Friendship.objects.create(from_user=self.user1, to_user=to_user)

        to_users = FriendshipService.get_to_users(self.user1.id)
        self.assertSetEqual(to_users, {self.user2.id, self.user3.id, self.user4.id})

        Friendship.objects.filter(from_user=self.user1, to_user=self.user2).delete()
        to_users = FriendshipService.get_to_users(self.user1.id)
        self.assertSetEqual(to_users, {self.user3.id, self.user4.id})
