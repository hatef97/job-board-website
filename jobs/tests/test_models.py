from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from jobs.models import Category, Tag, CompanyProfile, Job
from core.models import User



class CategoryModelTests(TestCase):


    def test_str_representation(self):
        """✅ __str__ returns the category name."""
        category = Category.objects.create(name="Technology")
        self.assertEqual(str(category), "Technology")


    def test_slug_is_auto_generated(self):
        """✅ Slug is auto-generated from name if not provided."""
        category = Category.objects.create(name="Data Science")
        self.assertEqual(category.slug, "data-science")


    def test_slug_is_not_overwritten_if_provided(self):
        """✅ Provided slug should not be overwritten on save."""
        category = Category.objects.create(name="Manual Slug", slug="custom-slug")
        self.assertEqual(category.slug, "custom-slug")


    def test_unique_slug_constraint(self):
        """✅ Slug uniqueness is enforced."""
        Category.objects.create(name="Design")
        with self.assertRaises(ValidationError):
            duplicate = Category(name="Design")
            duplicate.full_clean()  # Trigger uniqueness check


    def test_slugify_handles_special_characters(self):
        """✅ Slug generation strips special characters and spaces."""
        category = Category.objects.create(name="AI & Robotics 💡")
        self.assertEqual(category.slug, "ai-robotics")



class TagModelTests(TestCase):


    def test_str_representation(self):
        """✅ __str__ returns the tag name."""
        tag = Tag.objects.create(name="Python")
        self.assertEqual(str(tag), "Python")


    def test_name_uniqueness(self):
        """✅ Tag name must be unique."""
        Tag.objects.create(name="Remote")
        duplicate = Tag(name="Remote")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()  # triggers uniqueness validation


    def test_name_max_length(self):
        """✅ Tag name must not exceed 50 characters."""
        long_name = "x" * 51
        tag = Tag(name=long_name)
        with self.assertRaises(ValidationError):
            tag.full_clean()  # triggers max_length validation



class CompanyProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='employer@test.com', password='securepass', role='employer')


    def test_str_representation(self):
        """✅ __str__ should return company_name."""
        profile = CompanyProfile.objects.create(
            user=self.user,
            company_name="Django Inc.",
            location="New York"
        )
        self.assertEqual(str(profile), "Django Inc.")


    def test_one_to_one_user_link(self):
        """✅ Each user can have only one CompanyProfile."""
        CompanyProfile.objects.create(
            user=self.user,
            company_name="TechWorld",
            location="San Francisco"
        )
        with self.assertRaises(Exception):
            CompanyProfile.objects.create(
                user=self.user,
                company_name="DuplicateCo",
                location="LA"
            )


    def test_blank_optional_fields(self):
        """✅ Optional fields can be blank."""
        profile = CompanyProfile.objects.create(
            user=self.user,
            company_name="Optional Fields Test",
            location="Tehran"
        )
        self.assertEqual(profile.website, "")
        self.assertFalse(profile.logo)
        self.assertEqual(profile.description, "")


    def test_required_fields_validation(self):
        """✅ company_name and location are required."""
        profile = CompanyProfile(user=self.user)
        with self.assertRaises(ValidationError):
            profile.full_clean()  # This checks required fields before saving



class JobModelTests(TestCase):

    def setUp(self):
        self.employer = User.objects.create_user(email='employer@example.com', password='test123', role='employer')
        self.category = Category.objects.create(name="Engineering")
        self.tag1 = Tag.objects.create(name="Remote")
        self.tag2 = Tag.objects.create(name="Backend")


    def create_job(self, **kwargs):
        defaults = {
            "employer": self.employer,
            "title": "Senior Python Developer",
            "description": "Develop scalable web apps.",
            "location": "Tehran",
            "job_type": "full_time",
            "experience_level": "senior",
        }
        defaults.update(kwargs)
        return Job.objects.create(**defaults)


    def test_str_returns_title(self):
        job = self.create_job()
        self.assertEqual(str(job), "Senior Python Developer")


    def test_required_fields(self):
        job = Job(employer=self.employer)  # missing required fields
        with self.assertRaises(ValidationError):
            job.full_clean()


    def test_optional_fields_blank(self):
        job = self.create_job(requirements="", salary_min=None, salary_max=None, deadline=None, category=None)
        self.assertEqual(job.requirements, "")
        self.assertIsNone(job.salary_min)
        self.assertIsNone(job.salary_max)
        self.assertIsNone(job.deadline)
        self.assertIsNone(job.category)


    def test_valid_choices_for_job_type(self):
        job = self.create_job(job_type="contract")
        self.assertEqual(job.job_type, "contract")


    def test_invalid_job_type_choice_raises(self):
        job = self.create_job(job_type="gig")
        with self.assertRaises(ValidationError):
            job.full_clean()


    def test_valid_experience_level_choice(self):
        job = self.create_job(experience_level="junior")
        self.assertEqual(job.experience_level, "junior")


    def test_invalid_experience_level_choice_raises(self):
        job = self.create_job(experience_level="expert")
        with self.assertRaises(ValidationError):
            job.full_clean()


    def test_salary_decimal_range(self):
        job = self.create_job(salary_min=Decimal("3000.00"), salary_max=Decimal("6000.00"))
        self.assertEqual(job.salary_min, Decimal("3000.00"))
        self.assertEqual(job.salary_max, Decimal("6000.00"))


    def test_created_and_updated_timestamps(self):
        job = self.create_job()
        now = timezone.now()
        self.assertLessEqual(job.created_at, now)
        self.assertLessEqual(job.updated_at, now)


    def test_many_to_many_tags_assignment(self):
        job = self.create_job()
        job.tags.set([self.tag1, self.tag2])
        self.assertIn(self.tag1, job.tags.all())
        self.assertIn(self.tag2, job.tags.all())


    def test_deadline_field_accepts_valid_date(self):
        tomorrow = date.today() + timedelta(days=1)
        job = self.create_job(deadline=tomorrow)
        self.assertEqual(job.deadline, tomorrow)
