from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from booking.settings import GOOGLE_MAPS_API_KEY
from rooms.models import Room, Building, RoomRule
from rooms.forms import RoomForm, BuildingForm, RoomRuleInlineFormSet, RoomRuleForm


class DetailRoomView(TemplateView):
    template_name = "rooms/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # hide this key before commit
        context["API_KEY"] = GOOGLE_MAPS_API_KEY

        room_id = kwargs["room_id"]
        if room_id is None:
            raise Http404
        try:
            room = Room.objects.get(pk=room_id)
        except:
            raise Http404
        context["room"] = room
        context["building"] = room.building
        context["roomRules"] = RoomRule.objects.filter(room=room).order_by("day")
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

class EditRoomView(TemplateView):
    template_name = "rooms/edit.html"

    permission_required = "rooms.change_room"


    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        # hide this key before commit
        context["API_KEY"] = GOOGLE_MAPS_API_KEY

        CAN_CHANGE_BUILDING = self.request.user.has_perm("building.change_building")
        CAN_CHANGE_RULES = self.request.user.has_perm("roomRule.change_roomRule")

        context["changeRoomRules"] = CAN_CHANGE_RULES

        modify_room = kwargs["editRoomOrBuilding"]%2 == 1
        modify_building = kwargs["editRoomOrBuilding"] > 1

        context["modify_building"] = modify_building


        if self.request.method == "GET":
            if "room_id" in kwargs and kwargs["room_id"]:
                try:
                    room = Room.objects.all().get(pk=kwargs["room_id"])
                except:
                    raise Http404
                roomForm = RoomForm(instance=room)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(instance=room)
                context["edit"] = True
            else:
                roomForm = RoomForm()
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet()
        elif self.request.method == "POST":
            if "room_id" in kwargs and kwargs["room_id"]:
                try:
                    room = Room.objects.all().get(pk=kwargs["room_id"])
                except:
                    raise Http404
                roomForm = RoomForm(self.request.POST, instance=room)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(self.request.POST, instance=room)
            else:
                roomForm = RoomForm(self.request.POST)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(self.request.POST)
            context["edit"] = kwargs["edit"]
        else:
            raise Http404

        context["roomForm"] = roomForm
        if CAN_CHANGE_RULES:
            context["roomRuleForm"] = roomRuleForms
        """
        if (CAN_CHANGE_BUILDING):
            if self.request.method == "GET":
                if "room_id" in kwargs and kwargs["room_id"]:
                    try:
                        building = room.building
                    except:
                        raise Http404
                    buildingForm = BuildingForm(instance=building)
                    context["edit"] = True
                else:
                    buildingForm = BuildingForm()
            elif self.request.method == "POST":
                if "room_id" in kwargs and kwargs["room_id"]:
                    try:
                        building = Building.objects.all().get(pk=room__building__id)
                    except:
                        raise Http404
                    buildingForm = BuildingForm(self.request.POST, instance=room)
                else:
                    buildingForm = BuildingForm(self.request.POST)
                context["edit"] = kwargs["edit"]
            else:
                raise Http404
            context["buildingForm"] = buildingForm    """
        return context

#problem if the user cannot change rules but only rooms
    def post(self, request, *args, **kwargs):
        CAN_CHANGE_RULES = self.request.user.has_perm("roomRule.change_roomRule")

        if "room_id" in kwargs and kwargs["room_id"]:
            try:
                room = Room.objects.all().get(pk=kwargs["room_id"])
            except:
                raise Http404
            roomForm = RoomForm(request.POST, instance=room)
            if CAN_CHANGE_RULES:
                roomRuleForms = RoomRuleInlineFormSet(request.POST, instance=room)
            kwargs["edit"] = True
        else:
            roomForm = RoomForm(request.POST)
            if CAN_CHANGE_RULES:
                roomRuleForms = RoomRuleInlineFormSet(request.POST)
            kwargs["edit"] = False

        if roomForm.is_valid() and (roomRuleForms.is_valid() or not CAN_CHANGE_RULES):
            if CAN_CHANGE_RULES:
                room = roomForm.save()
            if kwargs["edit"]:
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(room).pk,
                    object_id=room.id,
                    object_repr=str(room),
                    action_flag=CHANGE
                )
            else:
                room = form.save(commit=False)
                room.creator = request.user
                room.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(room).pk,
                    object_id=room.id,
                    object_repr=str(room),
                    action_flag=ADDITION
                )
            return HttpResponseRedirect(reverse("rooms:details", kwargs={'room_id': room.pk}))
        else:
            return self.get(request, *args, **kwargs)
