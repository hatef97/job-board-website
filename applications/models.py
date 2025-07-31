from django.db import models
from django.conf import settings

from jobs.models import Job



class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-created_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'

    def __str__(self):
        return f'{self.applicant} → {self.job.title}'



class InterviewSchedule(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews_scheduled')
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    meeting_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Interview Schedule'
        verbose_name_plural = 'Interview Schedules'

    def __str__(self):
        return f'Interview for {self.application.applicant} on {self.date.strftime("%Y-%m-%d %H:%M")}'
        