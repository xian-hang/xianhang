from django.contrib import admin
from .models import Report, ReportNotice

class ReportAdmin(admin.ModelAdmin):
    list_display = ('user','reporting','status')

class ReportNoticeAdmin(admin.ModelAdmin):
    list_display = ('report','content')


# Register your models here.
admin.site.register(Report, ReportAdmin)
admin.site.register(ReportNotice, ReportNoticeAdmin)
