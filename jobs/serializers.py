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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = CompanyProfile
        fields = [
            'id', 'user', 'user_email', 'company_name', 'website',
            'logo', 'logo_url', 'location', 'description'
        ]
        read_only_fields = ['user']

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



class JobDetailSerializer(serializers.ModelSerializer):
    employer_email = serializers.EmailField(source='employer.email', read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source='tags', write_only=True, required=False
    )

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'requirements', 'location',
            'job_type', 'experience_level', 'salary_min', 'salary_max',
            'category', 'category_id', 'tags', 'tag_ids', 'deadline',
            'is_active', 'created_at', 'updated_at', 'employer_email'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        job = Job.objects.create(**validated_data)
        job.tags.set(tags)
        return job

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
        