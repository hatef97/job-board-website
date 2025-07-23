from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User, EmployerProfile, ApplicantProfile



# Inline for Employer Profile
class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = 'Employer Profile'



# Inline for Applicant Profile
class ApplicantProfileInline(admin.StackedInline):
    model = ApplicantProfile
    can_delete = False
    verbose_name_plural = 'Applicant Profile'



# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2'),
        }),
    )

    inlines = []

    def get_inlines(self, request, obj):
        if obj is None:
            return []
        return [EmployerProfileInline] if obj.role == 'employer' else [ApplicantProfileInline]



# Employer Profile Admin
@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'company_website', 'created_at')
    search_fields = ('company_name', 'user__email')
    readonly_fields = ('created_at',)



# Applicant Profile Admin
@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    