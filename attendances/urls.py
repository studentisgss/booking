from django.conf.urls import include, url
from attendances.views import *

app_name = "attendances"

urlpatterns = [
    url(r'^register/(?P<justsaved>\d|)$', GalileianAttendanceRegister.as_view(), name="register"),
    url(r'^foreign_register$', ForeignAttendanceRegister.as_view(), name="foreign_register"),
]
