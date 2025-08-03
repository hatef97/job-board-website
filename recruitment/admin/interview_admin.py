from django.contrib import admin
from django.utils.html import format_html

from recruitment.models import InterviewSchedule



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
