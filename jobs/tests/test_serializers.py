from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

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
            "company_name": "NextGen",
            "website": "https://nextgen.io",
            "location": "Toronto",
            "description": "Future of tech."
        }
        serializer = CompanyProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save(user=self.user)  # ✅ pass user here
        self.assertEqual(profile.company_name, "NextGen")
        self.assertEqual(profile.user, self.user)



class JobListSerializerTests(TestCase):

    def setUp(self):
        self.employer = User.objects.create_user(
            email='employer@example.com', password='securepass', role='employer'
        )
        self.category = Category.objects.create(name="Engineering")
        self.tag1 = Tag.objects.create(name="Python")
        self.tag2 = Tag.objects.create(name="Remote")

        self.job = Job.objects.create(
            employer=self.employer,
            title="Senior Backend Developer",
            description="Build APIs and services",
            location="Remote",
            job_type="full_time",
            experience_level="senior",
            salary_min=Decimal("5000.00"),
            salary_max=Decimal("8000.00"),
            category=self.category,
            deadline=date.today() + timedelta(days=30),
            is_active=True
        )
        self.job.tags.set([self.tag1, self.tag2])


    def test_job_list_serializer_output(self):
        """✅ Serializes Job with nested category, tags, and employer_email."""
        serializer = JobListSerializer(instance=self.job)
        data = serializer.data

        # Basic fields
        self.assertEqual(data['title'], "Senior Backend Developer")
        self.assertEqual(data['location'], "Remote")
        self.assertEqual(data['job_type'], "full_time")
        self.assertEqual(data['experience_level'], "senior")

        # Nested category
        self.assertEqual(data['category']['id'], self.category.id)
        self.assertEqual(data['category']['name'], "Engineering")
        self.assertEqual(data['category']['slug'], "engineering")

        # Tags
        tag_names = [tag['name'] for tag in data['tags']]
        self.assertIn("Python", tag_names)
        self.assertIn("Remote", tag_names)
        self.assertEqual(len(data['tags']), 2)

        # Computed field
        self.assertEqual(data['employer_email'], self.employer.email)

        # Optional fields
        self.assertTrue("created_at" in data)
        self.assertTrue("deadline" in data)



class JobDetailSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='employer@example.com', password='securepass', role='employer'
        )
        self.category = Category.objects.create(name="Engineering")
        self.tag1 = Tag.objects.create(name="Python")
        self.tag2 = Tag.objects.create(name="Remote")

        self.job = Job.objects.create(
            employer=self.user,
            title="Backend Dev",
            description="REST APIs",
            requirements="Python, DRF",
            location="Remote",
            job_type="full_time",
            experience_level="mid",
            salary_min=Decimal("4000.00"),
            salary_max=Decimal("7000.00"),
            category=self.category,
            deadline=date.today(),
            is_active=True
        )
        self.job.tags.set([self.tag1])


    def test_serialize_job_detail(self):
        """✅ Serializes job with nested and computed fields correctly."""
        serializer = JobDetailSerializer(instance=self.job)
        data = serializer.data

        self.assertEqual(data["title"], "Backend Dev")
        self.assertEqual(data["employer_email"], self.user.email)
        self.assertEqual(data["category"]["name"], "Engineering")
        self.assertEqual(data["tags"][0]["name"], "Python")
        self.assertNotIn("category_id", data)
        self.assertNotIn("tag_ids", data)


    def test_deserialize_and_create_job(self):
        """✅ Deserializes input and creates job with M2M (tag_ids) and FK (category_id)."""
        payload = {
            "title": "API Engineer",
            "description": "Build endpoints",
            "requirements": "DRF, Django",
            "location": "Hybrid",
            "job_type": "contract",
            "experience_level": "senior",
            "salary_min": "5000.00",
            "salary_max": "9000.00",
            "category_id": self.category.id,
            "tag_ids": [self.tag1.id, self.tag2.id],
            "deadline": str(date.today())
        }

        serializer = JobDetailSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        job = serializer.save(employer=self.user)

        self.assertEqual(job.title, "API Engineer")
        self.assertEqual(job.category, self.category)
        self.assertIn(self.tag1, job.tags.all())
        self.assertIn(self.tag2, job.tags.all())


    def test_update_job_tags_and_category(self):
        """✅ Updates a job with new tags and category."""
        new_category = Category.objects.create(name="DevOps")
        new_tag = Tag.objects.create(name="Kubernetes")

        payload = {
            "title": "Updated Title",
            "tag_ids": [new_tag.id],
            "category_id": new_category.id
        }

        serializer = JobDetailSerializer(instance=self.job, data=payload, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        job = serializer.save()

        self.assertEqual(job.title, "Updated Title")
        self.assertEqual(job.category, new_category)
        self.assertIn(new_tag, job.tags.all())
        self.assertNotIn(self.tag1, job.tags.all())  # Old tag removed


    def test_read_only_fields_not_updated(self):
        """✅ Ensures read-only fields are not updated."""
        original_created = self.job.created_at
        payload = {
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z"
        }

        serializer = JobDetailSerializer(instance=self.job, data=payload, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        job = serializer.save()

        self.assertEqual(job.created_at, original_created)  # Should not change
        self.assertNotEqual(str(job.updated_at.date()), "2000-01-01")
