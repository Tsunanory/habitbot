import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import Habit
from .serializers import UserSerializer, HabitSerializer
from django_celery_beat.models import PeriodicTask, CrontabSchedule

User = get_user_model()


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors)


@api_view(['POST'])
def login(request):
    serializer = UserSerializer(data=request.data)
    user = User.objects.filter(username=request.data.get('username')).first()
    if user and user.check_password(request.data.get('password')):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=400)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


def create_periodic_task(habit):
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=habit.time.hour,
        minute=habit.time.minute,
        day_of_week='*',
        day_of_month='*',
        month_of_year='*'
    )


    PeriodicTask.objects.create(
        crontab=schedule,
        name=f"send-habit-reminder-{habit.id}",
        task='telegram_bot.tasks.send_habit_reminders',
        args=json.dumps([habit.id]),
    )


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Habit.objects.filter(user=self.request.user).order_by('id')
        is_pleasant = self.request.query_params.get('is_pleasant', None)
        if is_pleasant is not None:
            queryset = queryset.filter(is_pleasant=is_pleasant.lower() == 'true')
        return queryset

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        create_periodic_task(habit)


class HabitPublicListView(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by('id')


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by('id')
