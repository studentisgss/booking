from django.conf.urls import include, url
from attendances.views import *

app_name = "attendances"

urlpatterns = [
    url(r'^register/(?P<foo>\d)$', GalileianAttendanceRegister.as_view(), name="register"),  # keeping only for retrocompatibility
    url(r'^register/$', GalileianAttendanceRegister.as_view(), name="register"),
    url(r'^foreign_register$', ForeignAttendanceRegister.as_view(), name="foreign_register"),
    url(r'^extract_data$', ExtractData.as_view(), name="extract_data"),
    url(r'^extract/(?P<event>\d+)$', Extract.as_view(), name="extract"),
    url(r'^extract/$', Extract.as_view(), name="extract")
]
