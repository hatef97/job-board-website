from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from core.models import User
from core.serializers import UserSerializer
from core.permissions import IsAdminOrSelf  



class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=400)

        exists = User.objects.filter(email__iexact=email).exists()
        return Response({"exists": exists})



class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for admin/staff to manage users, and for users to access their profile.
    Djoser handles login/register — this is for internal dashboard or admin.
    """
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_staff and request.user != instance:
            return Response({"detail": "Permission denied."}, status=403)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user profile (optional; Djoser already provides /auth/users/me/)"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
