from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.models import User, EmployerProfile



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



class EmployerProfileViewSetTests(APITestCase):
    """Tests for EmployerProfileViewSet: list, retrieve, create, update, delete & permissions."""

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        # Ensure admin has 'employer' role if needed
        self.admin_user.role = 'employer'
        self.admin_user.save()

        self.employer_user = User.objects.create_user(
            username='employer',
            email='employer@test.com',
            password='password123'
        )
        self.employer_user.role = 'employer'
        self.employer_user.save()

        self.other_employer = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='password123'
        )
        self.other_employer.role = 'employer'
        self.other_employer.save()

        self.applicant_user = User.objects.create_user(
            username='applicant',
            email='applicant@test.com',
            password='password123'
        )
        self.applicant_user.role = 'applicant'
        self.applicant_user.save()

        # Create two employer profiles
        self.profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='TestCo',
            company_website='https://test.co',
            company_description='A test company'
        )
        self.other_profile = EmployerProfile.objects.create(
            user=self.other_employer,
            company_name='OtherCo',
            company_website='https://other.co',
            company_description='Another company'
        )

        # Named routes from your DefaultRouter
        self.list_url = reverse('employer-profiles-list')
        self.detail_url = lambda pk: reverse('employer-profiles-detail', kwargs={'pk': pk})


    def authenticate(self, user):
        self.client.force_authenticate(user=user)


    def test_unauthenticated_cannot_access(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_employer_can_list_own_profile(self):
        self.authenticate(self.employer_user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['user'], self.employer_user.pk)


    def test_admin_can_list_all_profiles(self):
        self.authenticate(self.admin_user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)


    def test_employer_can_retrieve_own_profile(self):
        self.authenticate(self.employer_user)
        res = self.client.get(self.detail_url(self.profile.pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['company_name'], 'TestCo')


    def test_employer_cannot_retrieve_other(self):
        self.authenticate(self.employer_user)
        res = self.client.get(self.detail_url(self.other_profile.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


    def test_admin_can_retrieve_any(self):
        self.authenticate(self.admin_user)
        res = self.client.get(self.detail_url(self.other_profile.pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_employer_can_create_profile(self):
        # Delete existing then create a new one
        self.profile.delete()
        self.authenticate(self.employer_user)

        payload = {
            'company_name':        'NewCo',
            'company_website':     'https://new.co',
            'company_description': 'Brand new',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(EmployerProfile.objects.filter(user=self.employer_user).exists())
        self.assertEqual(res.data['company_name'], 'NewCo')


    def test_applicant_cannot_create_profile(self):
        self.authenticate(self.applicant_user)
        payload = {
            'company_name':        'NewCo',
            'company_website':     'https://new.co',
            'company_description': 'Brand new',
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


    def test_owner_can_update_profile(self):
        self.authenticate(self.employer_user)
        res = self.client.patch(
            self.detail_url(self.profile.pk),
            {'company_name': 'UpdatedCo'},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.company_name, 'UpdatedCo')


    def test_employer_cannot_update_other(self):
        self.authenticate(self.employer_user)
        res = self.client.patch(
            self.detail_url(self.other_profile.pk),
            {'company_name': 'HackedCo'},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


    def test_admin_can_update_any(self):
        self.authenticate(self.admin_user)
        res = self.client.patch(
            self.detail_url(self.other_profile.pk),
            {'company_name': 'AdminCo'},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.company_name, 'AdminCo')


    def test_owner_can_delete_profile(self):
        self.authenticate(self.employer_user)
        res = self.client.delete(self.detail_url(self.profile.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EmployerProfile.objects.filter(pk=self.profile.pk).exists())


    def test_employer_cannot_delete_other(self):
        self.authenticate(self.employer_user)
        res = self.client.delete(self.detail_url(self.other_profile.pk))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


    def test_admin_can_delete_any(self):
        self.authenticate(self.admin_user)
        res = self.client.delete(self.detail_url(self.other_profile.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EmployerProfile.objects.filter(pk=self.other_profile.pk).exists())


    def test_cannot_modify_read_only_fields(self):
        self.authenticate(self.employer_user)
        original_created = self.profile.created_at.isoformat()

        res = self.client.patch(
            self.detail_url(self.profile.pk),
            {'created_at': '2000-01-01T00:00:00Z'},
            format='json'
        )
        # should be a validation error, not 404
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.created_at.isoformat(), original_created)
