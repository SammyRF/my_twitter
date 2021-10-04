from utils.caches.redis_client import RedisClient
from datetime import datetime
from django.conf import settings

TIME_STAMP_PATTERN = '{rl_prefix}:{api_path}:{api_name}:{user_id}:{current_time}'


class RateLimitHelper:

    @classmethod
    def check_limit(cls, api_path, api_name, user_id, hms):
        if not settings.RATE_LIMIT_ENABLE:
            return True
        
        conn = RedisClient.get_connection()
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        key = TIME_STAMP_PATTERN.format(
            rl_prefix=settings.RATE_LIMIT_PREFIX,
            api_path=api_path,
            api_name=api_name,
            user_id=user_id,
            current_time=current_time
        )
        if not conn.exists(key):
            conn.set(key, hms[1]) # right now only support minute
            conn.expire(key, 60) # rate limit based on minute
            return True
        return conn.decr(key) > 0
