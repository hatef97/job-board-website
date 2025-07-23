from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from core.serializers import UserSerializer, EmployerProfileSerializer, ApplicantProfileSerializer
from core.models import User, EmployerProfile, ApplicantProfile



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



class EmployerProfileSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='employer@example.com',
            password='securepass123',
            role='employer'
        )


    def test_employer_profile_serializer_valid_data(self):
        data = {
            'company_name': 'Test Company',
            'company_website': 'https://testcompany.com',
            'company_description': 'We build job boards.',
        }
        serializer = EmployerProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        profile = serializer.save(user=self.user)
        self.assertEqual(profile.company_name, 'Test Company')
        self.assertEqual(profile.company_website, 'https://testcompany.com')
        self.assertEqual(profile.company_description, 'We build job boards.')
        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.created_at)


    def test_missing_company_name_should_fail(self):
        data = {
            'company_website': 'https://test.com',
            'company_description': 'Some description'
        }
        serializer = EmployerProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)


    def test_optional_fields_can_be_blank(self):
        data = {
            'company_name': 'NoSite Inc',
        }
        serializer = EmployerProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)
        self.assertEqual(profile.company_name, 'NoSite Inc')
        self.assertEqual(profile.company_website, None)
        self.assertEqual(profile.company_description, None)


    def test_created_at_is_read_only(self):
        now = timezone.now()
        data = {
            'company_name': 'FakeTime Inc',
            'company_website': 'https://faketime.com',
            'company_description': 'Time travel biz',
            'created_at': now  # trying to override
        }
        serializer = EmployerProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)
        self.assertNotEqual(profile.created_at, now)  # Should not match


    def test_user_field_is_read_only(self):
        data = {
            'company_name': 'Hacked Inc',
            'user': 9999  # shouldn't be accepted
        }
        serializer = EmployerProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)
        self.assertEqual(profile.user, self.user)



class ApplicantProfileSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='applicant@example.com',
            password='securepass',
            role='applicant'
        )


    def test_applicant_profile_with_resume(self):
        resume_file = SimpleUploadedFile("cv.pdf", b"dummy content", content_type="application/pdf")
        data = {
            'bio': 'Experienced developer.',
            'resume': resume_file,
        }
        serializer = ApplicantProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        profile = serializer.save(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Experienced developer.')
        self.assertTrue(profile.resume.name.startswith('resumes/cv'))


    def test_applicant_profile_without_resume(self):
        data = {
            'bio': 'No file uploaded.',
        }
        serializer = ApplicantProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        profile = serializer.save(user=self.user)
        self.assertEqual(profile.bio, 'No file uploaded.')
        self.assertFalse(profile.resume)


    def test_resume_can_be_null(self):
        data = {
            'bio': 'Bio with null resume',
            'resume': None
        }
        serializer = ApplicantProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)
        self.assertIsNone(profile.resume.name)


    def test_created_at_is_read_only(self):
        now = timezone.now()
        data = {
            'bio': 'Testing created_at',
            'created_at': now  # Attempt to override
        }
        serializer = ApplicantProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)
        self.assertNotEqual(profile.created_at.isoformat(), now.isoformat())


    def test_user_field_is_read_only(self):
        data = {
            'bio': 'Injected user id',
            'user': 9999  # Should be ignored
        }
        serializer = ApplicantProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        profile = serializer.save(user=self.user)
        self.assertEqual(profile.user, self.user)
