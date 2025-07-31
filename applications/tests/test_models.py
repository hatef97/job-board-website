import tempfile

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from jobs.models import Job
from applications.models import Application
from core.models import User, EmployerProfile



class ApplicationModelTests(TestCase):

    def setUp(self):
        # Create users
        self.applicant = User.objects.create_user(
            email='applicant1@test.com', password='pass1234', role='applicant'
        )
        self.employer = User.objects.create_user(
            email='employer1@test.com', password='pass1234', role='employer'
        )

        # Create EmployerProfile manually
        self.company, _ = EmployerProfile.objects.get_or_create(
            user=self.employer,
            defaults={
                'company_name': 'NextGen Tech',
                'company_website': 'https://nextgen.io',
                'company_description': 'Tech for the future'
            }
        )

        # Create a job
        self.job = Job.objects.create(
            title='Senior Python Developer',
            description='Exciting opportunity...',
            employer=self.employer,
            location='Berlin'
        )

        # Dummy resume file
        self.resume = SimpleUploadedFile(
            name='resume.pdf',
            content=b'%PDF-1.4 fake content',
            content_type='application/pdf'
        )


    def test_create_application_successfully(self):
        """✅ Can create a valid application with resume and cover letter."""
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter="I'm very interested in this role."
        )
        self.assertEqual(app.status, 'submitted')
        self.assertIsNotNone(app.created_at)
        self.assertEqual(str(app), f'{self.applicant} → {self.job.title}')


    def test_duplicate_application_not_allowed(self):
        """❌ Cannot apply to the same job twice."""
        Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume
        )
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                job=self.job,
                applicant=self.applicant,
                resume=self.resume
            )


    def test_status_choices(self):
        """✅ Status field accepts only predefined choices."""
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            status='reviewed'
        )
        self.assertEqual(app.status, 'reviewed')


    def test_cover_letter_optional(self):
        """✅ Cover letter field is optional."""
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume
        )
        self.assertEqual(app.cover_letter, '')


    def test_resume_upload_path(self):
        """✅ Resume is uploaded to correct directory."""
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume
        )
        self.assertTrue(app.resume.name.startswith('resumes/'))
