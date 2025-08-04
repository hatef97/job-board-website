from datetime import date
from decimal import Decimal

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from recruitment.models import *
from recruitment.serializers import *
from core.models import User  



class ApplicationViewSetTests(APITestCase):

    def setUp(self):
        # Create users
        self.employer = User.objects.create_user(username='employer', email='e@test.com', password='pass', role='employer')
        self.applicant = User.objects.create_user(username='applicant', email='a@test.com', password='pass', role='applicant')

        # Create a job
        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Developer',
            description='Django job',
            location='Remote',
            job_type='full_time',
            experience_level='junior'
        )

        self.resume = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4\n%Fake PDF file content\n%%EOF\n",
            content_type="application/pdf"
        )

        # Create an application
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter='Interested'
        )

        self.url = reverse('application-list')  # From DRF router


    def test_applicant_can_list_own_applications(self):
        self.client.force_authenticate(user=self.applicant)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert all(app['job_title'] == self.job.title for app in response.data)


    def test_employer_can_list_applications_to_their_jobs(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert any(app['job_title'] == self.job.title for app in response.data)


    def test_applicant_can_create_application(self):
        self.client.force_authenticate(user=self.applicant)

        another_job = Job.objects.create(
            employer=self.employer,
            title='Frontend Dev',
            description='Vue job',
            location='Remote',
            job_type='full_time',
            experience_level='junior'
        )

        data = {
            'job_id': another_job.id,
            'resume': SimpleUploadedFile(
                "resume.pdf",
                b"%PDF-1.4\n%Fake PDF file content\n%%EOF\n",
                content_type="application/pdf"
            ),
            'cover_letter': 'Please hire me'
        }

        response = self.client.post(self.url, data, format='multipart')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['job_title'] == another_job.title


    def test_employer_cannot_create_application(self):
        self.client.force_authenticate(user=self.employer)
        data = {
            'job_id': self.job.id,
            'resume': SimpleUploadedFile(
                "resume.pdf",
                b"%PDF-1.4\n%Fake PDF file content\n%%EOF\n",
                content_type="application/pdf"
            ),
            'cover_letter': 'I should not be allowed'
        }
        response = self.client.post(self.url, data, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_anonymous_user_cannot_access_applications(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_applicant_can_retrieve_own_application(self):
        self.client.force_authenticate(user=self.applicant)
        detail_url = reverse('application-detail', kwargs={'pk': self.application.pk})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.application.pk


    def test_employer_can_retrieve_application_to_their_job(self):
        self.client.force_authenticate(user=self.employer)
        detail_url = reverse('application-detail', kwargs={'pk': self.application.pk})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['job_title'] == self.job.title


    def test_applicant_cannot_see_other_users_applications(self):
        another_applicant = User.objects.create_user(username='another', email='x@test.com', password='pass', role='applicant')
        self.client.force_authenticate(user=another_applicant)
        detail_url = reverse('application-detail', kwargs={'pk': self.application.pk})
        response = self.client.get(detail_url)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]



class InterviewScheduleViewSetTests(APITestCase):
    def setUp(self):
        # Create users
        self.employer = User.objects.create_user(
            username='employer', email='emp@test.com', password='pass', role='employer'
        )
        self.applicant = User.objects.create_user(
            username='applicant', email='app@test.com', password='pass', role='applicant'
        )

        # Create job and application
        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Dev',
            description='Build APIs',
            location='Remote',
            job_type='full_time',
            experience_level='junior'
        )

        self.resume = SimpleUploadedFile(
            "resume.pdf", b"%PDF-1.4 test pdf", content_type="application/pdf"
        )

        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter='Let me join'
        )

        # Create an interview
        self.interview = InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=timezone.now() + timezone.timedelta(days=3),
            location='Zoom',
            meeting_link='https://zoom.us/test-meeting',
            notes='Discuss project experience'
        )

        self.url = reverse('interview-list')


    def test_authenticated_user_can_list_interviews(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


    def test_authenticated_user_can_retrieve_interview(self):
        self.client.force_authenticate(user=self.employer)
        detail_url = reverse('interview-detail', kwargs={'pk': self.interview.pk})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['application'] == self.application.id


    def test_employer_can_schedule_interview(self):
        self.client.force_authenticate(user=self.employer)
        new_job = Job.objects.create(
            employer=self.employer,
            title='New Job',
            description='Second opportunity',
            location='Remote',
            job_type='full_time',
            experience_level='junior'
        )

        new_application = Application.objects.create(
            job=new_job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter='Second app'
        )

        data = {
            'application': new_application.id,
            'date': (timezone.now() + timezone.timedelta(days=5)).isoformat(),
            'location': 'Google Meet',
            'meeting_link': 'https://meet.google.com/abc-defg-hij',
            'notes': 'Tech interview'
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


    def test_applicant_cannot_schedule_interview(self):
        self.client.force_authenticate(user=self.applicant)
        data = {
            'application': self.application.id,
            'scheduled_by': self.applicant.id,  # Trying to spoof
            'date': (timezone.now() + timezone.timedelta(days=5)).isoformat(),
            'location': 'Discord',
            'meeting_link': 'https://discord.com/meeting',
            'notes': 'Applicant tries scheduling'
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]


    def test_anonymous_user_cannot_access(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED



class ApplicantNoteViewSetTests(APITestCase):

    def setUp(self):
        # Create users
        self.employer = User.objects.create_user(username='employer', email='e@test.com', password='pass', role='employer')
        self.applicant = User.objects.create_user(username='applicant', email='a@test.com', password='pass', role='applicant')

        # Create job and application
        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Developer',
            description='Build APIs',
            location='Remote',
            job_type='full_time',
            experience_level='mid'
        )

        self.resume = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test content\n", content_type="application/pdf")

        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter="Excited to join"
        )

        # Create a note
        self.note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note='Great candidate'
        )

        self.list_url = reverse('note-list')
        self.detail_url = reverse('note-detail', kwargs={'pk': self.note.pk})


    def test_employer_can_list_notes(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert any(note['note'] == self.note.note for note in response.data)


    def test_applicant_cannot_see_notes(self):
        self.client.force_authenticate(user=self.applicant)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # No notes visible to applicants


    def test_employer_can_create_note(self):
        self.client.force_authenticate(user=self.employer)
        data = {
            'application': self.application.id,
            'note': 'Very promising candidate.'
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['note'] == 'Very promising candidate.'


    def test_applicant_cannot_create_note(self):
        self.client.force_authenticate(user=self.applicant)
        data = {
            'application': self.application.id,
            'note': 'Trying to add a note'
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]


    def test_employer_can_retrieve_note(self):
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['note'] == self.note.note


    def test_applicant_cannot_retrieve_note(self):
        self.client.force_authenticate(user=self.applicant)
        response = self.client.get(self.detail_url)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]



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



class CompanyProfileViewSetTests(APITestCase):

    def setUp(self):
        self.employer = User.objects.create_user(email="employer@test.com", password="password123", role="employer")
        self.applicant = User.objects.create_user(email="applicant@test.com", password="password123", role="applicant")

        self.profile = CompanyProfile.objects.create(
            user=self.employer,
            company_name="BirdTech",
            location="Berlin",
            description="We build smart birdhouses."
        )

        self.list_url = reverse("company-profile-list")
        self.detail_url = reverse("company-profile-detail", kwargs={"pk": self.profile.pk})


    def test_employer_can_list_own_profile(self):
        """✅ Employers can list only their own company profile."""
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company_name"], "BirdTech")


    def test_employer_can_retrieve_own_profile(self):
        """✅ Employers can retrieve their own profile."""
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "BirdTech")


    def test_applicant_cannot_access_profiles(self):
        """❌ Applicants should not access company profiles."""
        self.client.force_authenticate(user=self.applicant)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_anonymous_user_cannot_access_profiles(self):
        """❌ Anonymous users should be rejected."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_employer_can_create_profile(self):
        """✅ Employers can create their own profile."""
        new_employer = User.objects.create_user(
            email="newemployer@test.com", password="pass123", role="employer"
        )
        self.client.force_authenticate(user=new_employer)

        payload = {
            "company_name": "FeatherSoft",
            "location": "London",
            "description": "Bird-loving AI company"
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "FeatherSoft")
        self.assertEqual(response.data["user_email"], new_employer.email)


    def test_applicant_cannot_create_profile(self):
        """❌ Applicants should not be allowed to create profiles."""
        self.client.force_authenticate(user=self.applicant)

        payload = {
            "company_name": "WrongRole Inc",
            "location": "Nowhere",
            "description": "Not allowed"
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_employer_cannot_create_multiple_profiles(self):
        """❌ Employer cannot create a second company profile."""
        self.client.force_authenticate(user=self.employer)

        payload = {
            "company_name": "AnotherCo",
            "location": "Paris",
            "description": "Duplicate test"
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class JobViewSetTests(APITestCase):

    def setUp(self):
        self.employer = User.objects.create_user(
            email="employer@test.com", password="pass123", role="employer"
        )
        self.applicant = User.objects.create_user(
            email="applicant@test.com", password="pass123", role="applicant"
        )
        self.category = Category.objects.create(name="Engineering")
        self.tag1 = Tag.objects.create(name="Remote")
        self.tag2 = Tag.objects.create(name="Python")

        self.job = Job.objects.create(
            employer=self.employer,
            title="Senior Backend Developer",
            description="Build APIs",
            requirements="Python, DRF",
            location="Remote",
            job_type="full_time",
            experience_level="senior",
            salary_min=Decimal("5000.00"),
            salary_max=Decimal("9000.00"),
            category=self.category,
            deadline=date.today(),
            is_active=True
        )
        self.job.tags.set([self.tag1, self.tag2])

        self.list_url = reverse("job-list")
        self.detail_url = reverse("job-detail", kwargs={"pk": self.job.pk})


    def test_public_can_list_active_jobs(self):
        """✅ Unauthenticated users can list active jobs."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Senior Backend Developer")


    def test_employer_can_create_job(self):
        """✅ Employers can post a new job."""
        self.client.force_authenticate(user=self.employer)

        payload = {
            "title": "API Developer",
            "description": "Create RESTful endpoints",
            "requirements": "Django, DRF",
            "location": "Hybrid",
            "job_type": "contract",
            "experience_level": "mid",
            "salary_min": "4000.00",
            "salary_max": "7000.00",
            "category_id": self.category.id,
            "tag_ids": [self.tag1.id],
            "deadline": str(date.today())
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "API Developer")
        self.assertEqual(response.data["employer_email"], self.employer.email)


    def test_applicant_cannot_post_job(self):
        """❌ Applicants should not be able to create jobs."""
        self.client.force_authenticate(user=self.applicant)

        payload = {
            "title": "Unauthorized Job",
            "description": "This should fail",
            "location": "Nowhere",
            "job_type": "remote",
            "experience_level": "junior",
            "category_id": self.category.id
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_employer_sees_only_own_jobs(self):
        """✅ Employer can only see jobs they created."""
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for job in response.data:
            self.assertEqual(job["employer_email"], self.employer.email)


    def test_applicant_cannot_create_job(self):
        """❌ Applicants should not be able to create jobs (POST is forbidden)."""
        self.client.force_authenticate(user=self.applicant)

        payload = {
            "title": "Unauthorized Post",
            "description": "Should fail",
            "location": "Remote",
            "job_type": "remote",
            "experience_level": "junior",
            "category_id": self.category.id
        }

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_employer_can_retrieve_own_job(self):
        """✅ Employer can retrieve detail of own job."""
        self.client.force_authenticate(user=self.employer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.job.title)


    def test_anonymous_user_can_retrieve_job(self):
        """✅ Public user can view job detail if active."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.job.title)


    def test_applicant_can_view_jobs(self):
        """✅ Applicants should be allowed to view job listings."""
        self.client.force_authenticate(user=self.applicant)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
