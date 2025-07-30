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
