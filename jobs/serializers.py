from rest_framework import serializers

from .models import Category, Tag, CompanyProfile, Job
from core.models import User



# ==========================
# CATEGORY
# ==========================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']



# ==========================
# TAG
# ==========================

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
