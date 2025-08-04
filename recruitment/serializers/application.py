from rest_framework import serializers

from recruitment.models import Application, Job, InterviewSchedule, ApplicantNote



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
        read_only_fields = ['status', 'created_at', 'updated_at', 'applicant']

    def validate(self, data):
        job = data.get('job')
        applicant = self.context['request'].user
        if self.instance is None and Application.objects.filter(job=job, applicant=applicant).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return data



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



class ApplicantNoteSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    applicant_username = serializers.CharField(source='application.applicant.username', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)

    class Meta:
        model = ApplicantNote
        fields = [
            'id',
            'application',
            'applicant_username',
            'job_title',
            'author',
            'note',
            'created_at',
        ]
        read_only_fields = ['created_at', 'applicant_username', 'job_title']
