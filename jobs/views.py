from django.shortcuts import get_object_or_404

from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

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
        if CompanyProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a company profile.")
        serializer.save(user=self.request.user)



class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("employer", "category").prefetch_related("tags").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list']:
            return JobListSerializer
        return JobDetailSerializer

    def get_queryset(self):
        # Public read access
        if self.request.method in permissions.SAFE_METHODS:
            return self.queryset.filter(is_active=True)

        # Employers see their own jobs
        if self.request.user.role == 'employer':
            return self.queryset.filter(employer=self.request.user)
        raise PermissionDenied("Only employers can manage jobs.")

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise PermissionDenied("Only employers can post jobs.")
        serializer.save(employer=self.request.user)
