import accounts.api.serializers
from accounts.models import UserProfile
from django.contrib.auth.models import User
from utils.cache_helpers import USER_PATTERN, USER_PROFILE_PATTERN, project_cache


class UserService:

    @classmethod
    def get_user_through_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)

        # get user from cache first
        user = project_cache.get(key)
        if user:
            return user

        # if not found in cache, go to sql
        try:
            user = User.objects.get(id=user_id)
            project_cache.set(key, user)
        except User.DoesNotExist:
            user = None
        return user

    @classmethod
    def invalidate_user(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        project_cache.delete(key)

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

