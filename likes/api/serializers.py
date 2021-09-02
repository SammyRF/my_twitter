from accounts.api.serializers import UserSerializer
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Like
        fields = ('id', 'user', 'object_id', 'created_at')


class LikeSerializerForCreate(serializers.ModelSerializer):
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

    def create(self, validated_data):
        model_class = self.choices.get(validated_data['content_type'])
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['user'],
        )
        return instance
