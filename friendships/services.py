from friendships.models import Friendship
from utils.caches.cache_helpers import TO_USERS_PATTERN, project_cache


class FriendshipService:
    @classmethod
    def get_to_users(cls, from_user_id):
        key = TO_USERS_PATTERN.format(from_user_id=from_user_id)
        to_users = project_cache.get(key)
        if to_users is not None:
            return to_users

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        to_users = set([
            fs.to_user_id
            for fs in friendships
        ])
        project_cache.set(key, to_users)
        return to_users

    @classmethod
    def invalidate_to_users_cache(cls, from_user_id):
        key = TO_USERS_PATTERN.format(from_user_id=from_user_id)
        project_cache.delete(key)
