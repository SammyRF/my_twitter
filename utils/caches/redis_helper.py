from django.conf import settings
from utils.caches.redis_client import RedisClient
from utils.caches.redis_serializers import DjangoModelSerializer

USER_TWEETS_PATTERN = 'user_tweets:{user_id}'
USER_NEWSFEEDS_PATTERN = 'user_newsfeeds:{user_id}'


class RedisHelper:

    @classmethod
    def get_objects_from_redis(cls, key, queryset):
        conn = RedisClient.get_connection()

        # if redis hit
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            return [DjangoModelSerializer.deserialize(obj_data) for obj_data in serialized_list]

        # when not hit, load objects into redis
        objects = list(queryset)
        serialized_list = [DjangoModelSerializer.serialize(obj) for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]]
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return objects

    @classmethod
    def extend_object_in_redis(cls, key, obj, queryset):
        conn = RedisClient.get_connection()

        # if redis hit
        if conn.exists(key):
            serialized_obj = DjangoModelSerializer.serialize(obj)
            conn.lpush(key, serialized_obj)
            conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)
            return

        # if not hit, load from DB
        serialized_list = [DjangoModelSerializer.serialize(obj) for obj in queryset]
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def get_count_key(cls, obj, attr):
        return f'{obj.__class__.__name__}.{attr}:{obj.id}'

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if not conn.exists(key):
            obj.refresh_from_db()
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.incr(key)

    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if not conn.exists(key):
            obj.refresh_from_db()
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.decr(key)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if not conn.exists(key):
            obj.refresh_from_db()
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return int(conn.get(key))
