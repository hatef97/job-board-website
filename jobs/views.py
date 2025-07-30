from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import *
from .serializers import *

from core.models import User
from django.shortcuts import get_object_or_404



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]



class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.select_related("user").all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Employers can only see their own profile
        if self.request.user.role == 'employer':
            return self.queryset.filter(user=self.request.user)
        raise PermissionDenied("Only employers can access their company profile.")

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can create a company profile.")
        serializer.save(user=self.request.user)
