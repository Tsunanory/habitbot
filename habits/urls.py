from django.urls import path
from .views import register, login, HabitListCreateView, HabitPublicListView, HabitRetrieveUpdateDestroyView, \
    UserDetailView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('users/me/', UserDetailView.as_view(), name='user-detail'),
    path('habits/', HabitListCreateView.as_view(), name='habit-list-create'),
    path('habits/public/', HabitPublicListView.as_view(), name='habit-public-list'),
    path('habits/<int:pk>/', HabitRetrieveUpdateDestroyView.as_view(), name='habit-detail'),
]
