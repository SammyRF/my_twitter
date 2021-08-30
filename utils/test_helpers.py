from django.contrib.auth.models import User
from tweets.models import Tweet
from friendships.models import Friendship
from comments.models import Comment


class TestHelpers:

    @classmethod
    def create_user(cls, username='admin', password='correct password', email='admin@admin.com'):
        return User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

    @classmethod
    def create_tweet(cls, user, content='default tweet content'):
        return Tweet.objects.create(user=user, content=content)

    @classmethod
    def create_friendship(cls, from_user, to_user):
        return Friendship.objects.create(from_user=from_user, to_user=to_user)

    @classmethod
    def create_comment(cls, user, tweet, content="default comment content"):
        return Comment.objects.create(user=user, tweet=tweet, content=content)