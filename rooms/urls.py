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
from rooms.views import *

app_name = "rooms"

urlpatterns = [
    url(r'^detail/(?P<room_id>[0-9]+)$', DetailRoomView.as_view(), name="details"),
    url(r'^list/all$', ListAllRoomView.as_view(), name="listall"),
    url(r'^list/all/(?P<page>[0-9]+)$', ListAllRoomView.as_view(), name="listall"),
    url(r'^list$', ListRoomView.as_view(), name="list"),
    url(r'^list/(?P<page>[0-9]+)$', ListRoomView.as_view(), name="list"),
    url(r'^edit/(?P<room_id>[0-9]+)$', EditRoomView.as_view(), name="editRoom"),
    url(r'^new$', NewRoomView.as_view(), name="newRoom"),
    url(r'^editBuilding/(?P<building_id>[0-9]+)$', EditBuildingView.as_view(), name="editBuilding"),
]
