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



# ==========================
# COMPANY PROFILE
# ==========================

class CompanyProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'user', 'user_email', 'company_name', 'website',
            'logo', 'logo_url', 'location', 'description'
        ]

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None



# ==========================
# JOB
# ==========================

class JobListSerializer(serializers.ModelSerializer):
    employer_email = serializers.EmailField(source='employer.email', read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'location', 'job_type', 'experience_level',
            'salary_min', 'salary_max', 'category', 'tags',
            'deadline', 'is_active', 'created_at', 'employer_email'
        ]
