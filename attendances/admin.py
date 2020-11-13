from django.contrib import admin
from attendances.models import *

# Register your models here.

admin.site.register(GalileianAttendance)
admin.site.register(ForeignAttendance)
admin.site.register(Details)
admin.site.register(ExtractionLog)
