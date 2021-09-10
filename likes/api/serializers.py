from accounts.api.serializers import UserSerializerWithProfile
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from inbox.services import NotificationSerivce
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerWithProfile()

    class Meta:
        model = Like
        fields = ('id', 'user', 'object_id', 'created_at')


class LikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    choices = {'comment': Comment, 'tweet': Tweet}

    content_type = serializers.ChoiceField(choices=list(choices.keys()))
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def validate(self, attrs):
        model_class = self.choices.get(attrs['content_type'])
        if model_class is None:
            raise ValidationError({'content_type': 'content type not exists'})

        liked_obj = model_class.objects.filter(id=attrs['object_id']).first()
        if liked_obj is None:
            raise  ValidationError({'object_id': 'object not exists'})
        return attrs

class LikeSerializerForCreate(LikeSerializerForCreateAndCancel):
    def create(self, validated_data):
        model_class = self.choices.get(validated_data['content_type'])
        instance, created = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['user'],
        )
        if created:
            NotificationSerivce.send_like_notification(instance)
        return instance

class LikeSerializerForCancel(LikeSerializerForCreateAndCancel):
    def cancel(self):
        model_class = self.choices.get(self.validated_data['content_type'])
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['user'],
        ).delete()