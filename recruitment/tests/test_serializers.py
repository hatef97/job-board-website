import io
from datetime import date, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from recruitment.serializers import *
from recruitment.models import *
from core.models import User



class ApplicationSerializerTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='applicant1', email='applicant1@gmail.com', password='testpass')
        self.employer = User.objects.create_user(username='employer1', email='employer1@gmail.com', password='testpass', role='employer')
        
        self.job = Job.objects.create(
            title='Backend Developer',
            description='Build APIs',
            location='Remote',
            employer=self.employer
        )

        self.resume_file = SimpleUploadedFile(
            "resume.pdf", b"%PDF-1.4 resume content here", content_type="application/pdf"
        )

    def get_request(self, user=None):
        """Helper to generate a DRF-like request context"""
        request = self.factory.post('/fake-url/')
        request.user = user or self.user
        return request


    def test_valid_application_serialization(self):
        """✅ It should serialize and create a valid application."""
        data = {
            'job_id': self.job.id,
            'resume': self.resume_file,
            'cover_letter': "I am excited to apply!",
        }
        serializer = ApplicationSerializer(data=data, context={'request': self.get_request()})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        app = serializer.save()

        self.assertEqual(app.job, self.job)
        self.assertEqual(app.applicant, self.user)
        self.assertEqual(app.cover_letter, data['cover_letter'])
        self.assertEqual(app.status, 'submitted')
        self.assertIn('resumes/', app.resume.name)
        self.assertTrue(app.resume.name.endswith('.pdf'))


    def test_duplicate_application_validation(self):
        """🚫 It should not allow the same user to apply to the same job twice."""
        Application.objects.create(
            job=self.job,
            applicant=self.user,
            resume=self.resume_file,
            cover_letter='Original submission'
        )

        data = {
            'job_id': self.job.id,
            'resume': self.resume_file,
            'cover_letter': "Duplicate attempt",
        }
        serializer = ApplicationSerializer(data=data, context={'request': self.get_request()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


    def test_applicant_is_hidden_field(self):
        """🔒 Applicant should be auto-set from the request context."""
        data = {
            'job_id': self.job.id,
            'resume': self.resume_file,
            'cover_letter': "Please consider me",
        }
        serializer = ApplicationSerializer(data=data, context={'request': self.get_request()})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['applicant'], self.user)


    def test_resume_file_upload(self):
        """📁 Resume field should accept and store uploaded file properly."""
        data = {
            'job_id': self.job.id,
            'resume': self.resume_file,
            'cover_letter': "Attached resume.",
        }
        serializer = ApplicationSerializer(data=data, context={'request': self.get_request()})
        self.assertTrue(serializer.is_valid())
        app = serializer.save()
        self.assertIn('resumes/', app.resume.name)
        self.assertTrue(app.resume.name.endswith('.pdf'))



class InterviewScheduleSerializerTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        # Create users
        self.employer = User.objects.create_user(username='employer1', email='employer1@gmail.com', password='testpass', role='employer')
        self.applicant = User.objects.create_user(username='applicant1', email='applicant1@gmail.com', password='pass', role='applicant')

        # Create job and application
        self.job = Job.objects.create(
            title='Django Dev',
            description='Build Django apps',
            location='Remote',
            employer=self.employer,
        )

        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf"),
            cover_letter="Please interview me"
        )

        self.context = {'request': self._get_request(self.employer)}

    def _get_request(self, user):
        request = self.factory.post('/fake-url/')
        request.user = user
        return request


    def test_create_valid_interview_schedule(self):
        """✅ It should create a valid InterviewSchedule object."""
        data = {
            'application': self.application.id,
            'date': timezone.now() + timezone.timedelta(days=1),
            'location': "Zoom",
            'meeting_link': "https://zoom.us/fake-link",
            'notes': "Be prepared to talk about REST."
        }
        serializer = InterviewScheduleSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        interview = serializer.save()

        self.assertEqual(interview.application, self.application)
        self.assertEqual(interview.scheduled_by, self.employer)
        self.assertEqual(interview.location, data['location'])
        self.assertEqual(interview.meeting_link, data['meeting_link'])


    def test_duplicate_interview_validation(self):
        """🚫 It should prevent scheduling a second interview for the same application."""
        InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=timezone.now() + timezone.timedelta(days=2),
            location='Google Meet'
        )

        data = {
            'application': self.application.id,
            'date': timezone.now() + timezone.timedelta(days=3),
            'location': "Another call"
        }

        serializer = InterviewScheduleSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('application', serializer.errors)

        self.assertTrue(
            any("already exists" in str(msg) for msg in serializer.errors['application']),
            msg="Expected uniqueness error message."
        )


    def test_scheduled_by_is_auto_assigned(self):
        """🔒 It should auto-set scheduled_by from the request context."""
        data = {
            'application': self.application.id,
            'date': timezone.now() + timezone.timedelta(days=1),
            'location': "Online",
        }
        serializer = InterviewScheduleSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['scheduled_by'], self.employer)



class ApplicantNoteSerializerTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.employer = User.objects.create_user(username='employer1', email='employer1@gmail.com', password='testpass', role='employer')
        self.applicant = User.objects.create_user(username='applicant1', email='applicant1@gmail.com', password='pass', role='applicant')

        self.job = Job.objects.create(
            title='Full Stack Dev',
            description='Build web apps',
            location='Remote',
            employer=self.employer,
        )

        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=SimpleUploadedFile("cv.pdf", b"%PDF test", content_type="application/pdf"),
            cover_letter="Hire me"
        )

        self.context = {'request': self._get_request(self.employer)}


    def _get_request(self, user):
        request = self.factory.post('/fake-url/')
        request.user = user
        return request


    def test_create_valid_note(self):
        """✅ It should serialize and create a valid applicant note."""
        data = {
            'application': self.application.id,
            'note': 'Promising candidate with good experience.'
        }
        serializer = ApplicantNoteSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        note = serializer.save()
        self.assertEqual(note.application, self.application)
        self.assertEqual(note.author, self.employer)
        self.assertEqual(note.note, data['note'])


    def test_author_is_set_from_context(self):
        """🔒 The author field should be set automatically from the request user."""
        data = {
            'application': self.application.id,
            'note': 'Follows up promptly.'
        }
        serializer = ApplicantNoteSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['author'], self.employer)


    def test_read_only_fields_are_present(self):
        """🧠 The summary fields (job title, applicant) should be present in serialized output."""
        note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note='Detail-oriented and skilled.'
        )
        serializer = ApplicantNoteSerializer(note)

        self.assertEqual(serializer.data['job_title'], self.job.title)
        self.assertEqual(serializer.data['applicant_username'], self.applicant.username)
        self.assertIn('created_at', serializer.data)



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
