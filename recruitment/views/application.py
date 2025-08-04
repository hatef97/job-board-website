from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from recruitment.models import Application
from recruitment.serializers import ApplicationSerializer



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
        