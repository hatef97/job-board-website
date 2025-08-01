from django.contrib import admin
from django.utils.html import format_html

from .models import Application



@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'applicant_username',
        'job_title',
        'status',
        'created_at',
        'resume_download_link',
    )
    list_filter = (
        'status',
        ('job', admin.RelatedOnlyFieldListFilter),
        ('applicant', admin.RelatedOnlyFieldListFilter),
        'created_at',
    )
    search_fields = (
        'applicant__username',
        'applicant__email',
        'job__title',
        'cover_letter',
    )
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('created_at', 'updated_at', 'resume_download_link')
        return ('created_at', 'updated_at')

    def get_fieldsets(self, request, obj=None):
        base_fields = ('job', 'applicant', 'status')
        detail_fields = ['cover_letter', 'resume']
        if obj:
            detail_fields.append('resume_download_link')

        return (
            ('Application Info', {'fields': base_fields}),
            ('Details', {'fields': detail_fields}),
            ('Timestamps', {'fields': ('created_at', 'updated_at')}),
        )

    def applicant_username(self, obj):
        return obj.applicant.username
    applicant_username.short_description = "Applicant"

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = "Job"

    def resume_download_link(self, obj):
        if obj.resume:
            return format_html("<a href='{}' target='_blank' download>📄 Download Resume</a>", obj.resume.url)
        return "—"
    resume_download_link.short_description = "Resume"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'applicant')
        