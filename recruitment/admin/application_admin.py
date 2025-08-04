from django.contrib import admin
from django.utils.html import format_html

from recruitment.models import Application, InterviewSchedule, ApplicantNote



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



@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'application_id',
        'applicant_name',
        'job_title',
        'scheduled_by',
        'date',
        'meeting_link_display',
    )
    list_filter = (
        ('scheduled_by', admin.RelatedOnlyFieldListFilter),
        'date',
    )
    search_fields = (
        'application__applicant__username',
        'application__applicant__email',
        'application__job__title',
        'location',
        'notes',
    )
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('application_summary',)

    fieldsets = (
        (None, {
            'fields': ('application', 'scheduled_by', 'date', 'location', 'meeting_link', 'notes')
        }),
        ('Application Summary', {
            'fields': ('application_summary',)
        }),
    )

    def applicant_name(self, obj):
        return obj.application.applicant.username
    applicant_name.short_description = "Applicant"

    def job_title(self, obj):
        return obj.application.job.title
    job_title.short_description = "Job"

    def meeting_link_display(self, obj):
        if obj.meeting_link:
            return format_html("<a href='{}' target='_blank'>🔗 Link</a>", obj.meeting_link)
        return "—"
    meeting_link_display.short_description = "Meeting Link"

    def application_summary(self, obj):
        app = obj.application
        return format_html(
            "<b>Applicant:</b> {}<br><b>Job:</b> {}<br><b>Status:</b> {}<br><b>Resume:</b> {}",
            app.applicant.username,
            app.job.title,
            app.status,
            format_html("<a href='{}' download>📄 Resume</a>", app.resume.url) if app.resume else "—"
        )
    application_summary.short_description = "Application Info"
    application_summary.allow_tags = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'application__applicant',
            'application__job',
            'scheduled_by'
        )



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
        