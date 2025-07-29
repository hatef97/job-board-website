from django.test import TestCase
from django.core.exceptions import ValidationError

from jobs.models import Category



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