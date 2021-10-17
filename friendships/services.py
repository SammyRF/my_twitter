from friendships.models import Friendship
from utils.memcached.memcached_helper import TO_USERS_PATTERN, project_memcached


class FriendshipService:
    @classmethod
    def get_to_users_in_memcached(cls, from_user_id):
        key = TO_USERS_PATTERN.format(from_user_id=from_user_id)
        to_users = project_memcached.get(key)
        if to_users is not None:
            return to_users

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        to_users = set([
            fs.to_user_id
            for fs in friendships
        ])
        project_memcached.set(key, to_users)
        return to_users

    @classmethod
    def invalidate_to_users_in_memcached(cls, from_user_id):
        key = TO_USERS_PATTERN.format(from_user_id=from_user_id)
        project_memcached.delete(key)
