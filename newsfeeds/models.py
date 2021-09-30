from django.contrib.auth.models import User
from django.db import models
from tweets.models import Tweet
from utils.caches.memcached_helper import MemcachedHelper


class NewsFeed(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.tweet}'

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)


def extend_newsfeed_in_redis(sender, instance, created, **kwargs):
    if not created:
        return

    from newsfeeds.services import NewsFeedService
    NewsFeedService.extend_cached_newsfeed(instance)

models.signals.post_save.connect(extend_newsfeed_in_redis, sender=NewsFeed)