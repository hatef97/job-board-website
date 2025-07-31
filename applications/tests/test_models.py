import tempfile

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError

from jobs.models import Job
from applications.models import Application, InterviewSchedule
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



class InterviewScheduleModelTests(TestCase):

    def setUp(self):
        # Create users
        self.applicant = User.objects.create_user(
            email='applicant@test.com', password='pass1234', role='applicant'
        )
        self.employer = User.objects.create_user(
            email='employer@test.com', password='pass1234', role='employer'
        )

        # 🚫 Clean up existing profile
        EmployerProfile.objects.filter(user=self.employer).delete()

        # Create employer profile
        self.company = EmployerProfile.objects.create(
            user=self.employer,
            company_name='TechCorp',
            company_website='https://techcorp.io',
            company_description='Innovative Tech Company'
        )

        # Create job
        self.job = Job.objects.create(
            title='Backend Developer',
            description='Work on APIs and services.',
            employer=self.employer,
            location='Berlin'
        )

        # Create application
        self.resume = SimpleUploadedFile('resume.pdf', b'resume content')
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume
        )


    def test_create_interview_schedule(self):
        """✅ Successfully creates a valid interview schedule."""
        interview = InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=timezone.now() + timezone.timedelta(days=2),
            location='Zoom',
            meeting_link='https://zoom.us/meeting/xyz',
            notes='Initial round'
        )
        self.assertIsInstance(interview, InterviewSchedule)
        self.assertEqual(interview.application, self.application)
        self.assertEqual(interview.scheduled_by, self.employer)
        self.assertEqual(interview.location, 'Zoom')


    def test_optional_fields_can_be_blank(self):
        """✅ Optional fields `meeting_link` and `notes` can be blank."""
        interview = InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=timezone.now() + timezone.timedelta(days=1),
            location='Onsite'
        )
        self.assertIsNone(interview.meeting_link)
        self.assertEqual(interview.notes, '')


    def test_one_to_one_constraint(self):
        """❌ Cannot assign two interviews to the same application."""
        InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=timezone.now() + timezone.timedelta(days=1),
            location='Online'
        )
        with self.assertRaises(IntegrityError):
            InterviewSchedule.objects.create(
                application=self.application,
                scheduled_by=self.employer,
                date=timezone.now() + timezone.timedelta(days=3),
                location='Zoom'
            )


    def test_str_representation(self):
        """✅ __str__ returns the correct format."""
        date = timezone.now() + timezone.timedelta(days=1)
        interview = InterviewSchedule.objects.create(
            application=self.application,
            scheduled_by=self.employer,
            date=date,
            location='Virtual'
        )
        expected = f'Interview for {self.applicant} on {date.strftime("%Y-%m-%d %H:%M")}'
        self.assertEqual(str(interview), expected)
