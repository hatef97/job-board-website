from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import User



class UserManagerTests(TestCase):
    

    def test_create_user_with_email_successful(self):
        email = 'testuser@example.com'
        password = 'strongpassword123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='testpass')


    def test_create_user_normalizes_email(self):
        email = 'User@Example.COM'
        user = User.objects.create_user(email=email, password='pass123')
        self.assertEqual(user.email, 'User@example.com')


    def test_create_superuser_successful(self):
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)


    def test_create_superuser_missing_flags_defaults_correctly(self):
        email = 'admin2@example.com'
        password = 'adminpass456'
        user = User.objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


    def test_str_representation(self):
        user = User.objects.create_user(email='test@example.com', password='test123', role='applicant')
        self.assertIn('test@example.com', str(user))



class UserModelTests(TestCase):


    def test_create_applicant_user(self):
        user = User.objects.create_user(
            email='applicant@example.com',
            password='securepass123',
            role='applicant',
            first_name='Ali',
            last_name='Applicant'
        )
        self.assertEqual(user.email, 'applicant@example.com')
        self.assertEqual(user.role, 'applicant')
        self.assertTrue(user.check_password('securepass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(str(user), 'applicant@example.com (applicant)')


    def test_create_employer_user(self):
        user = User.objects.create_user(
            email='employer@example.com',
            password='securepass456',
            role='employer',
            first_name='Elham',
            last_name='Employer'
        )
        self.assertEqual(user.role, 'employer')
        self.assertTrue(user.check_password('securepass456'))


    def test_create_user_without_email_should_fail(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='password')


    def test_email_uniqueness(self):
        User.objects.create_user(email='unique@example.com', password='pass1', role='applicant')
        with self.assertRaises(Exception):
            User.objects.create_user(email='unique@example.com', password='pass2', role='applicant')


    def test_create_superuser_defaults(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass',
            role='employer'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)


    def test_string_representation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='pass',
            role='applicant'
        )
        self.assertEqual(str(user), 'test@example.com (applicant)')


    def test_timestamps_are_set(self):
        user = User.objects.create_user(
            email='timecheck@example.com',
            password='timepass',
            role='applicant'
        )
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
