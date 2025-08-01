from rest_framework import serializers

from .models import Application
from jobs.models import Job



class ApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.HiddenField(default=serializers.CurrentUserDefault())
    resume = serializers.FileField(use_url=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), source='job')

    class Meta:
        model = Application
        fields = [
            'id',
            'job_id',
            'job_title',
            'applicant',
            'resume',
            'cover_letter',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate(self, data):
        """Prevent same user from applying to same job twice."""
        job = data.get('job')
        applicant = self.context['request'].user
        if self.instance is None and Application.objects.filter(job=job, applicant=applicant).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return data
