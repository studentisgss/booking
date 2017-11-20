from django.contrib import admin
from rooms.models import *

# Register your models here.

admin.site.register(Room)
admin.site.register(RoomPermission)
admin.site.register(Building)
