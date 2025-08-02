from rest_framework import viewsets, permissions

from recruitment.models import ApplicantNote
from recruitment.serializers import ApplicantNoteSerializer



class ApplicantNoteViewSet(viewsets.ModelViewSet):
    queryset = ApplicantNote.objects.select_related('application', 'author', 'application__job')
    serializer_class = ApplicantNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
