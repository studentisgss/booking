from django.contrib import admin
from django.contrib.admin.models import LogEntry

# Register your models here.

# Register log entry to monitor log in the admin interface
admin.site.register(LogEntry)
