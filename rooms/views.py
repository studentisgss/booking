from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from rooms.models import Room


class DetailRoomView(TemplateView):
    template_name = "rooms/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = kwargs["room_id"]
        if room_id is None:
            raise Http404
        try:
            room = Room.objects.get(pk=room_id)
        except:
            raise Http404
        context["room"] = room
        return context


class ListAllRoomView(TemplateView):
    template_name = "rooms/listall.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms_list = Room.objects.order_by("-important", "name")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            rooms_list = rooms_list.filter(
                Q(name__icontains=text) | Q(description__icontains=text)
            )
        paginator = Paginator(rooms_list, per_page=25)
        page = kwargs.get("page", 1)
        try:
            rooms = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page which is 1 not 0.
            rooms = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            rooms = paginator.page(paginator.num_pages)
        context["list"] = rooms
        return context


class ListRoomView(TemplateView):
    template_name = "rooms/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms_list = Room.objects.filter(important=True).order_by("name")
        # Check for filter-text
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            rooms_list = rooms_list.filter(
                Q(name__icontains=text) | Q(description__icontains=text)
            )
        context["list"] = rooms_list
        return context
