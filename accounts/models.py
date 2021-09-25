from django.contrib.auth.models import User
from django.db import models
from utils import helpers


class UserProfile(models.Model):
    avatar = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=100, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user}: {self.nickname}'

def get_profile(user):
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    user_profile = UserService.get_user_profile_through_cache(user.id)
    setattr(user, '_cached_user_profile', user_profile)
    return user_profile

User.profile = property(get_profile)


models.signals.pre_delete.connect(helpers.invalidate_object_cache, sender=User)
models.signals.post_save.connect(helpers.invalidate_object_cache, sender=User)

def on_user_profile_changed(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalidate_userprofile(instance.user_id)

models.signals.pre_delete.connect(on_user_profile_changed, sender=UserProfile)
models.signals.post_save.connect(on_user_profile_changed, sender=UserProfile)



