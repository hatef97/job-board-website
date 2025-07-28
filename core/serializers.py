from rest_framework import serializers

from django.contrib.auth import get_user_model

from core.models import User, EmployerProfile, ApplicantProfile



# -------------------------
# User Serializer
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'password', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['is_active', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')

        # 🔐 Non-admins can't change sensitive fields
        restricted_fields = ['email', 'role', 'is_staff', 'is_superuser']
        if not request or not getattr(request.user, 'is_staff', False):
            for field in restricted_fields:
                validated_data.pop(field, None)        
        
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance



# -------------------------
# Employer Profile Serializer
# -------------------------
class EmployerProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'user', 'company_name', 'company_website',
            'company_description', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        # If the client tried to set created_at, error out
        if 'created_at' in self.initial_data:
            raise serializers.ValidationError({
                'created_at': 'This field is read-only.'
            })
        return super().validate(attrs)



# -------------------------
# Applicant Profile Serializer
# -------------------------
class ApplicantProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ApplicantProfile
        fields = [
            'id', 'user', 'resume', 'bio', 'created_at'
        ]
        read_only_fields = ['created_at']
        