from django.conf import settings
from django.core.cache import caches

TO_USERS_PATTERN = 'to_users:{from_user_id}'
FROM_USERS_PATTERN = 'from_users:{to_user_id}'

project_cache = caches['testing'] if settings.TESTING else caches['default']
