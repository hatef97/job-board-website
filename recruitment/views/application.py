from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from recruitment.models import Application, InterviewSchedule, ApplicantNote
from recruitment.serializers import ApplicationSerializer, InterviewScheduleSerializer, ApplicantNoteSerializer



class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'employer':
            return Application.objects.filter(job__employer=user).select_related('job', 'applicant')
        return Application.objects.filter(applicant=user).select_related('job')

    def perform_create(self, serializer):
        if self.request.user.role != 'applicant':
            raise PermissionDenied("Only applicants can submit applications.")
        serializer.save(applicant=self.request.user)



class InterviewScheduleViewSet(viewsets.ModelViewSet):
    queryset = InterviewSchedule.objects.select_related('application', 'scheduled_by', 'application__job')
    serializer_class = InterviewScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]



class ApplicantNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicantNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'employer':
            return ApplicantNote.objects.none()  # Block applicants from seeing any notes
        return ApplicantNote.objects.select_related('application', 'author', 'application__job')\
                                    .filter(application__job__employer=user)

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can add notes.")
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can update notes.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can delete notes.")
        instance.delete()
