from django.contrib import admin

from recruitment.models import Category, Tag, CompanyProfile, Job



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)



@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'location')
    search_fields = ('company_name', 'user__email', 'location')
    autocomplete_fields = ('user',)
    list_filter = ('location',)
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" width="80" height="80" style="object-fit:cover;" />'
        return "-"
    logo_preview.allow_tags = True
    logo_preview.short_description = "Logo Preview"



@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'location', 'job_type', 'experience_level', 'is_active', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_active', 'category', 'tags')
    search_fields = ('title', 'description', 'location', 'employer__email')
    autocomplete_fields = ('employer', 'category', 'tags')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'employer', 'description', 'requirements')
        }),
        ('Job Details', {
            'fields': (
                'location', 'job_type', 'experience_level',
                ('salary_min', 'salary_max'),
                'category', 'tags', 'deadline', 'is_active'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    