"""activities URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from events.views import Agenda, Calendar, Monitor

app_name = "events"

urlpatterns = [
    url(r'^agenda/(?P<page>\d+)$', Agenda.as_view(), name="agenda"),
    url(r'^agenda$', Agenda.as_view(), name="agenda"),
    url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})$', Calendar.as_view(),
        name="calendar"),
    url(r'^calendar$', Calendar.as_view(), name="calendar"),
    url(r'^monitor$', Monitor.as_view(), name="monitor"),
]
