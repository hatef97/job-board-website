from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from core.models import User



class CheckEmailViewTests(APITestCase):

    def setUp(self):
        self.url = reverse("auth-check-email")
        self.existing_email = "test@example.com"
        User.objects.create_user(email=self.existing_email, password="pass123", role="applicant")


    def test_email_exists(self):
        """✅ Should return true for existing email (case-insensitive)."""
        response = self.client.post(self.url, {"email": "TEST@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"exists": True})


    def test_email_does_not_exist(self):
        """✅ Should return false for non-existent email."""
        response = self.client.post(self.url, {"email": "notfound@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"exists": False})


    def test_email_missing(self):
        """❌ Should return 400 if email is not provided."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Email is required.")


    def test_get_not_allowed(self):
        """❌ Should not allow GET method."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
