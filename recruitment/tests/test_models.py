import tempfile
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError

from recruitment.models import *
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



class ApplicantNoteModelTests(TestCase):

    def setUp(self):
        # Create users
        self.applicant = User.objects.create_user(
            email='applicant@test.com', password='pass1234', role='applicant'
        )
        self.employer = User.objects.create_user(
            email='employer@test.com', password='pass1234', role='employer'
        )

        # Ensure test isolation
        EmployerProfile.objects.filter(user=self.employer).delete()

        # Create employer profile
        self.company = EmployerProfile.objects.create(
            user=self.employer,
            company_name='FutureTech',
            company_website='https://futuretech.io',
            company_description='Innovating tomorrow'
        )

        # Create job
        self.job = Job.objects.create(
            title='Backend Engineer',
            description='Develop APIs and backend services.',
            employer=self.employer,
            location='Remote'
        )

        # Resume file
        self.resume = SimpleUploadedFile('resume.pdf', b'%PDF-resume')

        # Create application
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            resume=self.resume,
            cover_letter="Excited to join."
        )


    def test_create_note_successfully(self):
        """✅ Can create a note for an application."""
        note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="Strong portfolio and relevant experience."
        )
        self.assertEqual(note.application, self.application)
        self.assertEqual(note.author, self.employer)
        self.assertEqual(note.note, "Strong portfolio and relevant experience.")
        self.assertIsNotNone(note.created_at)


    def test_str_representation(self):
        """✅ __str__ should include author and applicant email."""
        note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="Excellent communication skills."
        )
        expected = f"Note by {self.employer} for {self.applicant}"
        self.assertEqual(str(note), expected)


    def test_ordering_by_created_at_desc(self):
        """✅ Notes should be ordered by most recent first."""
        old_note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="First impression: solid."
        )
        old_note.created_at = timezone.now() - timezone.timedelta(days=1)
        old_note.save()

        new_note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="Follow-up: confirmed interest."
        )

        notes = list(ApplicantNote.objects.filter(application=self.application))
        self.assertEqual(notes[0], new_note)
        self.assertEqual(notes[1], old_note)


    def test_note_cascade_delete_with_application(self):
        """✅ Deleting the application should delete its notes."""
        note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="Will recommend for interview."
        )
        self.application.delete()
        self.assertFalse(ApplicantNote.objects.filter(id=note.id).exists())


    def test_note_cascade_delete_with_user(self):
        """✅ Deleting the author should delete their notes."""
        note = ApplicantNote.objects.create(
            application=self.application,
            author=self.employer,
            note="Final comment."
        )
        self.employer.delete()
        self.assertFalse(ApplicantNote.objects.filter(id=note.id).exists())



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
