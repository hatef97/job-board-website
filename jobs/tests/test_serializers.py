from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.exceptions import ValidationError

from jobs.models import *
from jobs.serializers import *
from core.models import User



class CategorySerializerTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Development")


    def test_serialize_category(self):
        """✅ Serializing a Category instance returns correct fields."""
        serializer = CategorySerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(data['id'], self.category.id)
        self.assertEqual(data['name'], "Development")
        self.assertEqual(data['slug'], "development")


    def test_deserialize_valid_data(self):
        """✅ Valid data deserializes and saves correctly."""
        data = {"name": "Marketing"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(category.name, "Marketing")
        self.assertEqual(category.slug, "marketing")


    def test_slug_is_read_only(self):
        """✅ Slug cannot be manually set through serializer input."""
        data = {"name": "Design", "slug": "manual-slug"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertNotEqual(category.slug, "manual-slug")  # Should be auto-generated
        self.assertEqual(category.slug, "design")


    def test_duplicate_name_validation(self):
        """✅ Duplicate category names should raise a validation error."""
        data = {"name": "Development"}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)



class TagSerializerTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="Python")


    def test_serialize_tag(self):
        """✅ Serializing a Tag instance returns expected fields."""
        serializer = TagSerializer(instance=self.tag)
        data = serializer.data
        self.assertEqual(data['id'], self.tag.id)
        self.assertEqual(data['name'], "Python")


    def test_deserialize_valid_data(self):
        """✅ Valid data creates a new Tag instance."""
        data = {"name": "Django"}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        tag = serializer.save()
        self.assertEqual(tag.name, "Django")


    def test_duplicate_name_not_allowed(self):
        """✅ Duplicate tag names should raise a validation error."""
        data = {"name": "Python"}
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


    def test_max_length_validation(self):
        """✅ Tag name cannot exceed 50 characters."""
        data = {"name": "x" * 51}
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)



class CompanyProfileSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="employer@example.com",
            password="securepass",
            role="employer"
        )
        self.factory = RequestFactory()


    def test_serialize_profile_without_logo(self):
        """✅ Serializes profile without logo and includes user_email and null logo_url."""
        profile = CompanyProfile.objects.create(
            user=self.user,
            company_name="TechCorp",
            location="Tehran",
        )
        request = self.factory.get("/")
        serializer = CompanyProfileSerializer(instance=profile, context={"request": request})
        data = serializer.data

        self.assertEqual(data['user_email'], "employer@example.com")
        self.assertEqual(data['company_name'], "TechCorp")
        self.assertIsNone(data['logo_url'])


    def test_serialize_profile_with_logo(self):
        """✅ Serializes profile with logo and returns absolute logo_url."""
        logo = SimpleUploadedFile("logo.png", b"image-bytes", content_type="image/png")
        profile = CompanyProfile.objects.create(
            user=self.user,
            company_name="PixelSoft",
            location="NYC",
            logo=logo
        )
        request = self.factory.get("/")
        serializer = CompanyProfileSerializer(instance=profile, context={"request": request})
        data = serializer.data

        # Assert logo_url is a full URL and points to company_logos/
        self.assertIn("http://", data['logo_url'])
        self.assertIn("company_logos/", data['logo_url'])
        self.assertIn("logo", data['logo_url']) 


    def test_get_logo_url_without_request_context(self):
        """✅ logo_url is None if context has no request."""
        logo = SimpleUploadedFile("logo.png", b"image-bytes", content_type="image/png")
        profile = CompanyProfile.objects.create(
            user=self.user,
            company_name="NoRequest Inc.",
            location="Berlin",
            logo=logo
        )
        serializer = CompanyProfileSerializer(instance=profile)
        self.assertIsNone(serializer.data['logo_url'])


    def test_deserialize_valid_data(self):
        """✅ Can create a profile from valid data input."""
        data = {
            "user": self.user.id,
            "company_name": "NextGen",
            "website": "https://nextgen.io",
            "location": "Toronto",
            "description": "Future of tech."
        }
        serializer = CompanyProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()
        self.assertEqual(profile.company_name, "NextGen")
        self.assertEqual(profile.user, self.user)
