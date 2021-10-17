from accounts.api.serializers import UserSerializer, UserSerializerWithProfile
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.validators import ValidationError
from friendships.services import FriendshipService


class ToUsersMixin:
    @property
    def to_users_of_request_user(self: serializers.ModelSerializer):
        if self.context['user'].is_anonymous:
            return {}
        if hasattr(self, '_cached_to_users_of_request_user'):
            return self._cached_to_users_of_request_user
        to_users_of_request_user = FriendshipService.get_to_users_in_memcached(self.context['user'].id)
        setattr(self, '_cached_to_users_of_request_user', to_users_of_request_user)
        return to_users_of_request_user


class FriendshipSerializer(serializers.ModelSerializer, ToUsersMixin):
    from_user = UserSerializerWithProfile(source='cached_from_user')
    to_user = UserSerializerWithProfile(source='cached_to_user')
    created_at = serializers.DateTimeField()
    followed_from_user = serializers.SerializerMethodField()
    followed_to_user = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'to_user', 'created_at', 'followed_from_user', 'followed_to_user')

    def get_followed_from_user(self, obj):
        return obj.from_user_id in self.to_users_of_request_user

    def get_followed_to_user(self, obj):
        return obj.to_user_id in self.to_users_of_request_user


class FriendshipForCreateSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError({
                'message': 'user cannot follow himself',
            })
        return data

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(from_user_id=from_user_id, to_user_id=to_user_id)
