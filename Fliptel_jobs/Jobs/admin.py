from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Job

@admin.register(Job)
class JobAdmin(ImportExportModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'posted_date')
    search_fields = ('title', 'company', 'location')
    list_filter = ('job_type', 'posted_date')
