from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

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
        