from django.test import TestCase

from core.serializers import UserSerializer
from core.models import User



class UserSerializerTests(TestCase):

    def setUp(self):
        self.valid_user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'applicant',
            'password': 'securepass123',
        }

    def test_user_serializer_creates_user_successfully(self):
        serializer = UserSerializer(data=self.valid_user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.email, self.valid_user_data['email'])
        self.assertTrue(user.check_password(self.valid_user_data['password']))
        self.assertEqual(user.role, 'applicant')
        self.assertTrue(user.is_active)

    def test_password_is_write_only(self):
        serializer = UserSerializer(data=self.valid_user_data)
        serializer.is_valid()
        self.assertNotIn('password', serializer.data)

    def test_missing_required_fields_should_fail(self):
        invalid_data = {
            'email': '',
            'password': '',
            'role': '',
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('role', serializer.errors)

    def test_invalid_role_should_fail(self):
        invalid_data = {
            **self.valid_user_data,
            'role': 'manager',  # not in choices
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_user_update_with_password_change(self):
        user = User.objects.create_user(
            email='update@example.com',
            password='oldpass',
            role='applicant'
        )
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'password': 'newpass123',
        }
        serializer = UserSerializer(instance=user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertTrue(updated_user.check_password('newpass123'))
