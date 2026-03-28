from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

class RegistrationValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_registration_short_password(self):
        data = {
            "email": "test@example.com",
            "password": "Short1!",
            "confirm_password": "Short1!"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password must be at least 8 characters long.")

    def test_registration_no_uppercase(self):
        data = {
            "email": "test@example.com",
            "password": "lowercas1!",
            "confirm_password": "lowercas1!"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password must contain at least one uppercase letter.")

    def test_registration_no_number(self):
        data = {
            "email": "test@example.com",
            "password": "NoNumber!",
            "confirm_password": "NoNumber!"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password must contain at least one number.")

    def test_registration_no_special_char(self):
        data = {
            "email": "test@example.com",
            "password": "NoSpecial1",
            "confirm_password": "NoSpecial1"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password must contain at least one special character.")

    def test_registration_success(self):
        data = {
            "email": "valid@example.com",
            "password": "ValidPassword1!",
            "confirm_password": "ValidPassword1!"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully")

    def test_registration_duplicate_email(self):
        User.objects.create(email="dup@example.com", password="password123")
        data = {
            "email": "dup@example.com",
            "password": "ValidPassword1!",
            "confirm_password": "ValidPassword1!"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "A user with this email already exists.")
