from django.test import TestCase
from friendships.hbase_models import HBaseFromUser, HBaseToUser
from friendships.models import Friendship
from friendships.services import FriendshipService
from utils.test_helpers import TestHelpers
from utils.hbase.models.exceptions import EmptyColumnError, BadRowKeyError
import time


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

        to_users = FriendshipService.get_to_users_in_memcached(self.user1.id)
        self.assertSetEqual(to_users, {self.user2.id, self.user3.id, self.user4.id})

        Friendship.objects.filter(from_user=self.user1, to_user=self.user2).delete()
        to_users = FriendshipService.get_to_users_in_memcached(self.user1.id)
        self.assertSetEqual(to_users, {self.user3.id, self.user4.id})


class HBaseTests(TestCase):

    def setUp(self):
        TestHelpers.clear_cache()

    @property
    def ts_now(self):
        return int(time.time() * 1000000)

    def test_save_and_get(self):
        # test save
        ts = self.ts_now
        friendship = HBaseFromUser(from_user_id=123, to_user_id=456, created_at=ts)
        friendship.save()
        instance = HBaseFromUser.get(from_user_id=123, created_at=ts)
        self.assertEqual(instance.from_user_id, 123)
        self.assertEqual(instance.to_user_id, 456)
        self.assertEqual(instance.created_at, ts)

        friendship.to_user_id = 789
        friendship.save()
        instance = HBaseFromUser.get(from_user_id=123, created_at=ts)
        self.assertEqual(instance.from_user_id, 123)
        self.assertEqual(instance.to_user_id, 789)
        self.assertEqual(instance.created_at, ts)

        # test object not found
        instance = HBaseFromUser.get(from_user_id=123, created_at=self.ts_now)
        self.assertIsNone(instance)

    def test_create_and_get(self):
        # missing column data by create
        try:
            HBaseFromUser.create(from_user_id=123, created_at=self.ts_now)
            exception_raised = False
        except EmptyColumnError:
            exception_raised = True
        self.assertTrue(exception_raised)

        # missing row key by create
        try:
            HBaseFromUser.create(to_user_id=456, created_at=self.ts_now)
            exception_raised = False
        except BadRowKeyError:
            exception_raised = True
        self.assertTrue(exception_raised)

        ts = self.ts_now
        friendship = HBaseToUser(from_user_id=123, to_user_id=456, created_at=ts)
        friendship.save()
        instance = HBaseToUser.get(to_user_id=456, created_at=ts)
        self.assertEqual(instance.from_user_id, 123)
        self.assertEqual(instance.to_user_id, 456)
        self.assertEqual(instance.created_at, ts)

        # missing row key by get
        try:
            HBaseToUser.get(to_user_id=456)
            exception_raised = False
        except BadRowKeyError:
            exception_raised = True
        self.assertTrue(exception_raised)