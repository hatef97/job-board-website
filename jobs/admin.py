from django.contrib import admin

from .models import Category, Tag, CompanyProfile, Job



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
    