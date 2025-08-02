from rest_framework import serializers

from recruitment.models import InterviewSchedule



class InterviewScheduleSerializer(serializers.ModelSerializer):
    scheduled_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    applicant_username = serializers.CharField(source='application.applicant.username', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)

    class Meta:
        model = InterviewSchedule
        fields = [
            'id',
            'application',
            'applicant_username',
            'job_title',
            'scheduled_by',
            'date',
            'location',
            'meeting_link',
            'notes',
        ]
        read_only_fields = ['scheduled_by', 'applicant_username', 'job_title']

    def validate_application(self, value):
        if self.instance is None and InterviewSchedule.objects.filter(application=value).exists():
            raise serializers.ValidationError("This application already has an interview scheduled.")
        return value
