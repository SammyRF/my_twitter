from django.contrib.auth.models import User
from tweets.models import Tweet

class TestHelpers:

    @classmethod
    def create_user(cls, username='admin', password='correct password', email='admin@admin.com'):
        return User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

    @classmethod
    def create_tweet(cls, user, content='default content'):
        return Tweet.objects.create(user=user, content=content)