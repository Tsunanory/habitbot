from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Habit

# Model Tests


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place='Gym',
            time='07:00:00',
            action='Workout',
            is_pleasant=False,
            frequency=1,
            reward='Protein Shake',
            duration=10,
            is_public=True
        )
        self.assertEqual(habit.place, 'Gym')
        self.assertEqual(habit.action, 'Workout')
        self.assertFalse(habit.is_pleasant)
        self.assertEqual(habit.reward, 'Protein Shake')
        self.assertEqual(habit.duration, 10)
        self.assertTrue(habit.is_public)

# API Tests


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = APIClient()
        self.client.login(username='testuser', password='12345')
        self.habit = Habit.objects.create(
            user=self.user,
            place='Gym',
            time='07:00:00',
            action='Workout',
            is_pleasant=False,
            frequency=1,
            reward='Protein Shake',
            duration=10,
            is_public=True
        )
        self.habit_url = reverse('habit-detail', kwargs={'pk': self.habit.pk})

    def test_get_habit_list(self):
        url = reverse('habit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_habit(self):
        url = reverse('habit-list')
        data = {
            'user': self.user.id,
            'place': 'Park',
            'time': '08:00:00',
            'action': 'Jogging',
            'is_pleasant': False,
            'frequency': 1,
            'reward': 'Smoothie',
            'duration': 15,
            'is_public': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
        self.assertEqual(Habit.objects.get(id=response.data['id']).place, 'Park')

    def test_update_habit(self):
        data = {
            'place': 'Home',
            'time': '09:00:00',
            'action': 'Yoga',
            'is_pleasant': False,
            'frequency': 1,
            'reward': 'Tea',
            'duration': 20,
            'is_public': False
        }
        response = self.client.put(self.habit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.place, 'Home')
        self.assertEqual(self.habit.action, 'Yoga')

    def test_delete_habit(self):
        response = self.client.delete(self.habit_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)
