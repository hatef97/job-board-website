from rest_framework import viewsets, permissions

from recruitment.models import InterviewSchedule
from recruitment.serializers import InterviewScheduleSerializer



class InterviewScheduleViewSet(viewsets.ModelViewSet):
    queryset = InterviewSchedule.objects.select_related('application', 'scheduled_by', 'application__job')
    serializer_class = InterviewScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
