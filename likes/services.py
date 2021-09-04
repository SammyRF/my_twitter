from django.contrib.contenttypes.models import ContentType
from likes.models import Like


class LikeServices:
    @classmethod
    def has_like(cls, user, target):
        if user.is_anonymous:
            return False
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        ).exists()