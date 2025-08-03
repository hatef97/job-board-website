from django.contrib import admin
from django.utils.html import format_html

from recruitment.models import ApplicantNote



@admin.register(ApplicantNote)
class ApplicantNoteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'applicant_username',
        'job_title',
        'author',
        'short_note',
        'created_at',
    )
    list_filter = (
        ('author', admin.RelatedOnlyFieldListFilter),
        ('application__job', admin.RelatedOnlyFieldListFilter),
        ('application__applicant', admin.RelatedOnlyFieldListFilter),
        'created_at',
    )
    search_fields = (
        'note',
        'author__username',
        'author__email',
        'application__job__title',
        'application__applicant__username',
        'application__applicant__email',
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Note Info', {
            'fields': ('application', 'author', 'note')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def applicant_username(self, obj):
        return obj.application.applicant.username
    applicant_username.short_description = "Applicant"

    def job_title(self, obj):
        return obj.application.job.title
    job_title.short_description = "Job"

    def short_note(self, obj):
        return (obj.note[:50] + "...") if len(obj.note) > 50 else obj.note
    short_note.short_description = "Note Preview"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'application__applicant',
            'application__job',
            'author'
        )
        