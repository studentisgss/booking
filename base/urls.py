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
from events.views import Calendar
from base.views import ManagementView, CleanUserView, BackupView, GroupsMembersView

app_name = "base"

urlpatterns = [
    url(r'^$', Calendar.as_view()),
    url(r'^manage$', ManagementView.as_view(), name="management"),
    url(r'^manage/clean$', CleanUserView.as_view(), name="clean"),
    url(r'^manage/backup$', BackupView.as_view(), name="backup"),
    url(r'^manage/groups$', GroupsMembersView.as_view(), name="groups"),
    url(r'^manage/groups/add/(?P<pk>\d+)$', GroupsMembersView.as_view(),
        kwargs={"operation": "add"}, name="groups_add"),
    url(r'^manage/groups/remove/(?P<pk>\d+)$', GroupsMembersView.as_view(),
        kwargs={"operation": "remove"}, name="groups_remove"),
    url(r'^manage/groups/clear/(?P<pk>\d+)$', GroupsMembersView.as_view(),
        kwargs={"operation": "clear"}, name="groups_clear"),
]
