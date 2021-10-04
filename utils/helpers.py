from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
import pytz


def utc_now():
    return datetime.now().replace(tzinfo=pytz.utc)


def validation_errors_response(errors):
    return Response({
        'success': False,
        'message': 'Please check input',
        'errors': errors,
    }, status=status.HTTP_400_BAD_REQUEST)


def invalidate_object_cache(sender, instance, **kwargs):
    from utils.caches.memcached_helper import MemcachedHelper
    MemcachedHelper.invalidate_cached_object(sender, instance.id)
