import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from applications.serializers import *
from applications.models import *
from jobs.models import Job
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
