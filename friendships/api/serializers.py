from accounts.api.serializers import UserSerializer
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.validators import ValidationError


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    to_user = UserSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'to_user', 'created_at')


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
