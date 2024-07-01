from rest_framework import serializers
from .models import Habit
from users.models import CustomUser


class HabitSerializer(serializers.ModelSerializer):
    related_habit = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)

    def get_related_habit(self, obj):
        if obj.related_habit:
            return {
                'id': obj.related_habit.id,
                'action': obj.related_habit.action,
                'time': obj.related_habit.time,
                'place': obj.related_habit.place,
            }
        return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'telegram_id')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            telegram_id=validated_data.get('telegram_id', None)
        )
        return user
