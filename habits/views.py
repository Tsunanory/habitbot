from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Habit
from .serializers import UserSerializer, HabitSerializer


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


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Habit.objects.filter(user=self.request.user).order_by('id')
        is_pleasant = self.request.query_params.get('is_pleasant', None)
        if is_pleasant is not None:
            queryset = queryset.filter(is_pleasant=is_pleasant.lower() == 'true')
        return queryset

    def list(self, request, *args, **kwargs):
        no_pagination = self.request.query_params.get('no_pagination', 'false').lower() == 'true'
        if no_pagination:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
