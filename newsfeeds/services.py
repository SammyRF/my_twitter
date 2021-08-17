from friendships.models import Friendship
from newsfeeds.models import NewsFeed

def fan_out(user, tweet):
    # prefetch improved performance
    friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
    newsfeeds = [NewsFeed(user=friendship.from_user, tweet=tweet) for friendship in friendships]
    # add user self
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    # bulk_create improved performance
    NewsFeed.objects.bulk_create(newsfeeds)
    