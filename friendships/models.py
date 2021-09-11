from django.contrib.auth.models import User
from django.db import models

class Friendship(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="from_user_set")
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="to_user_set")

    class Meta:
        index_together = (('from_user_id', 'created_at'), ('to_user_id', 'created_at'))
        unique_together = (('from_user_id', 'to_user_id'), )

    def __str__(self):
        return f'{self.from_user.id} follows {self.to_user.id}'