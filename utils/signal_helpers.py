from django.db import models


def invalidate_object_cache(sender, instance, **kwargs):
    from utils.caches.cache_helpers import CacheHelper
    CacheHelper.invalidate_cached_object(sender, instance.id)


def register_model_changed(model_class, invalidate_func=invalidate_object_cache):
    models.signals.post_save.connect(invalidate_func, sender=model_class)
    models.signals.pre_delete.connect(invalidate_func, sender=model_class)