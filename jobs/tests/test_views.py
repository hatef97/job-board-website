from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from jobs.models import *
from jobs.serializers import *



class CategoryViewSetTests(APITestCase):

    def setUp(self):
        self.cat1 = Category.objects.create(name="Development")
        self.cat2 = Category.objects.create(name="Marketing")

        self.list_url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.cat1.pk})


    def test_list_categories(self):
        """✅ Should return all categories (public access)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        names = [cat['name'] for cat in response.data]
        self.assertIn("Development", names)
        self.assertIn("Marketing", names)


    def test_retrieve_single_category(self):
        """✅ Should return a specific category by ID (public access)."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.cat1.name)
        self.assertEqual(response.data['slug'], self.cat1.slug)


    def test_retrieve_nonexistent_category_returns_404(self):
        """✅ Should return 404 for invalid category ID."""
        bad_url = reverse("category-detail", kwargs={"pk": 999})
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_category_list_permission_is_public(self):
        """✅ Public (unauthenticated) users should access list view."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_category_detail_permission_is_public(self):
        """✅ Public (unauthenticated) users should access detail view."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class TagViewSetTests(APITestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(name="Remote")
        self.tag2 = Tag.objects.create(name="Python")

        self.list_url = reverse("tag-list")
        self.detail_url = reverse("tag-detail", kwargs={"pk": self.tag1.pk})


    def test_list_tags(self):
        """✅ Should return all tags (public access)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        tag_names = [tag['name'] for tag in response.data]
        self.assertIn("Remote", tag_names)
        self.assertIn("Python", tag_names)


    def test_retrieve_single_tag(self):
        """✅ Should return a specific tag by ID."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Remote")


    def test_nonexistent_tag_returns_404(self):
        """✅ Should return 404 for invalid tag ID."""
        url = reverse("tag-detail", kwargs={"pk": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_tag_list_permission_is_public(self):
        """✅ Unauthenticated users should access tag list."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_tag_detail_permission_is_public(self):
        """✅ Unauthenticated users should access tag detail."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
