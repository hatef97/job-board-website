from django.db import models
from django.conf import settings

from .application import Application



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
