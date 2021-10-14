from accounts.models import UserProfile
from utils.memcached.memcached_helper import USER_PROFILE_PATTERN, project_cache


class UserService:

    @classmethod
    def get_user_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)

        # get userprofile from cache first
        userprofile = project_cache.get(key)
        if userprofile:
            return userprofile

        # if not found in cache, go to sql
        userprofile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        project_cache.set(key, userprofile)
        return userprofile

    @classmethod
    def invalidate_userprofile(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        project_cache.delete(key)

