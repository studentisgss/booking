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
from news.views import NewsView, NewsEditView, NewsAddView, NewsDeleteView, MessageView
from news.feeds import RssNewsFeed, AtomNewsFeed

app_name = "news"

urlpatterns = [
    url(r'^$', NewsView.as_view(), name="news"),
    url(r'^new$', NewsAddView.as_view(), name="new"),
    url(r'^edit/(?P<pk>\d+)$', NewsEditView.as_view(), name="edit"),
    url(r'^delete/(?P<pk>\d+)$', NewsDeleteView.as_view(), name="delete"),

    url(r'^messages/(?P<activity_id>\d+)$', MessageView.as_view(), name="messages"),

    url(r'^feed/rss$', RssNewsFeed(), name="rss"),
    url(r'^feed/atom$', AtomNewsFeed(), name="atom"),
]
