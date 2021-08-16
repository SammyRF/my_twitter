from rest_framework import serializers
from friendships.models import Friendship
from accounts.api.serializers import UserSerializer
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

    def validate(self, attrs):
        print(attrs)
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'user cannot follow himself',
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(from_user_id=from_user_id, to_user_id=to_user_id)