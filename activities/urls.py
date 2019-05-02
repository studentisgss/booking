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
from django.views.decorators.cache import cache_page
from activities.views import *
from activities.feeds import *

app_name = "activities"

urlpatterns = [
    url(r'^detail/(?P<activity_id>[0-9]+)$', DetailActivityView.as_view(), name="details"),
    url(r'^list/all/(?P<clas>[A-Z]+)$', ListAllActivityView.as_view(), name="listall"),
    url(r'^list/all$', ListAllActivityView.as_view(), name="listall"),
    url(r'^list/(?P<clas>[A-Z]+)$', ListNotArchivedActivityView.as_view(), name="list"),
    url(r'^list$', ListNotArchivedActivityView.as_view(), name="list"),

    url(r'^new$', ActivityAddView.as_view(), name="new"),
    url(r'^edit/(?P<pk>\d+)$', ActivityEditView.as_view(), name="edit"),
    url(r'^edit/events/(?P<pk>\d+)$', ActivityManagerEditView.as_view(), name="editmanager"),

    url(r'^bookeddates$', BookedDatesAPI.as_view(), name="bookeddates"),
    url(r'^bookedhours$', BookedHoursAPI.as_view(), name="bookedhours"),

    url(r'^feed/rss/(?P<activity_id>[0-9]+)$',
        cache_page(15 * 60)(RssActivityFeed()), name="rss"),
    url(r'^feed/atom/(?P<activity_id>[0-9]+)$',
        cache_page(15 * 60)(AtomActivityFeed()), name="atom"),
    url(r'^feed/ics/(?P<activity_id>[0-9]+)$',
        cache_page(15 * 60)(ICalActivityFeed.as_view()), name="ics"),
]
