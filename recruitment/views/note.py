from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from recruitment.models import ApplicantNote
from recruitment.serializers import ApplicantNoteSerializer



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
