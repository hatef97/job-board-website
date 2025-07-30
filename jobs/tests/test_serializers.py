from django.test import TestCase

from rest_framework.exceptions import ValidationError

from jobs.models import Category
from jobs.serializers import CategorySerializer
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
