from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from .models import User

class ForgotPasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="test@example.com", password="password123")
        self.url = reverse('forgot-password')

    def test_forgot_password_success(self):
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password sent to your email successfully.")
        
        # Verify email was "sent" to outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your Password Recovery")
        self.assertIn("password123", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])

    def test_forgot_password_user_not_found(self):
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "User with this email does not exist.")
        self.assertEqual(len(mail.outbox), 0)
