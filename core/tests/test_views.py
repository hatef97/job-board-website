from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase, APIClient
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



class UserViewSetTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass", role="employer")
        self.user1 = User.objects.create_user(email="user1@example.com", password="testpass", role="applicant", first_name="Ali")
        self.user2 = User.objects.create_user(email="user2@example.com", password="testpass", role="applicant", first_name="Hassan")

        self.client = APIClient()


    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)


    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_can_view_self_detail(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-detail', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user1.email)


    def test_user_cannot_view_other_user_detail(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_can_update_self(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-detail', kwargs={'pk': self.user1.pk})
        response = self.client.patch(url, {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')


    def test_user_cannot_update_other_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.patch(url, {'first_name': 'Blocked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_admin_can_delete_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_user_cannot_delete_other_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-detail', kwargs={'pk': self.user2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_me_endpoint(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('users-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user1.email)


    def test_search_user_by_first_name(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-list') + '?search=Ali'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Ali" in u['first_name'] for u in response.data))
