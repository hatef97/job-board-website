from django.db import models
from django.conf import settings

from .application import Application



class ApplicantNote(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applicant_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Applicant Note'
        verbose_name_plural = 'Applicant Notes'

    def __str__(self):
        return f'Note by {self.author} for {self.application.applicant}'
