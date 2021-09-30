from django.conf import settings
from django.core.cache import caches

TO_USERS_PATTERN = 'to_users:{from_user_id}'
USER_PROFILE_PATTERN = 'userprofile:{user_id}'

project_cache = caches['testing'] if settings.TESTING else caches['default']


class CacheHelper:
    @classmethod
    def get_key(cls, model_class, object_id):
        return '{}:{}'.format(model_class.__name__, object_id)

    @classmethod
    def get_object_through_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)

        # cache hit
        obj = project_cache.get(key)
        if obj:
            return obj

        # cache miss
        obj = model_class.objects.filter(id=object_id).first()
        if obj:
            project_cache.set(key, obj)

        return obj

    @classmethod
    def invalidate_cached_object(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        project_cache.delete(key)
