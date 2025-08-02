from rest_framework import serializers

from recruitment.models import ApplicantNote



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
