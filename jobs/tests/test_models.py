from django.test import TestCase
from django.core.exceptions import ValidationError

from jobs.models import Category, Tag, CompanyProfile
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
