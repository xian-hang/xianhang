from django.contrib import admin
from .models import XHUser

# Register your models here.
class XHUserAdmin(admin.ModelAdmin):
    list_display = ('username','role','studentId','status')

admin.site.register(XHUser,XHUserAdmin)