"""booking URL Configuration

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
from django.conf.urls import include, url, handler404, handler500
from django.contrib import admin

from activities import urls as activities_urls
from base import urls as base_urls
from events import urls as events_urls
from news import urls as news_urls
from rooms import urls as rooms_urls

urlpatterns = [
    # Admin site
    url(r'^admin/', admin.site.urls),

    url(r'^activities/', include(activities_urls, namespace="activities")),
    url(r'^events/', include(events_urls, namespace="events")),
    url(r'^news/', include(news_urls, namespace="news")),
    url(r'^rooms/', include(rooms_urls, namespace="rooms")),
    # If none of the above urls matches, then
    url(r'', include(base_urls)),
]

# The comment 'noqa: xxx' tells Flake8 to ignore the given error on the line
handler404 = "base.views.page_not_found"  # noqa: F811
handler500 = "base.views.server_error"  # noqa: F811
