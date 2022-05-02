from django.contrib import admin
from .models import Report

class ReportAdmin(admin.ModelAdmin):
    list_display = ('user','reporting','status')

# Register your models here.
admin.site.register(Report, ReportAdmin)
