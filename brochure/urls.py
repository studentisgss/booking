from django.conf.urls import include, url
from brochure.views import *

app_name = "brochure"

urlpatterns = [
    url(r'(?P<category>([A-z])\w)$', BrochurePDFView.as_view(), name="pdf")
]
