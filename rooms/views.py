from collections import OrderedDict

from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from booking.settings import GOOGLE_MAPS_API_KEY
from rooms.models import Room, Building, RoomRule
from rooms.forms import RoomForm, BuildingForm, RoomRuleInlineFormSet, RoomRuleForm


class DetailRoomView(TemplateView):
    template_name = "rooms/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This key is needed for using google maps api
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
    template_name = "rooms/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all"] = True  # This flag will adapt the template
        # Create a dictionary where the keys are the buildings
        # and the value is a queryset with the rooms in the building
        list = OrderedDict([])
        # Check for filter-text
        if "search" in self.request.GET:  # Search the text in the buildings and in the rooms's name
                                        # (not in the description or address for now)
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            list = OrderedDict([])
            for building in Building.objects.order_by(
                "-room__important"
            ).distinct().order_by("name"):
                # if the text match with a building then return all the romms of the building
                if building.name.lower().find(text.lower()) != -1:
                    list[building] = building.room_set.order_by("-important", "name")
                else:  # return only the rooms that have the text in the name
                    rooms = building.room_set.filter(Q(name__icontains=text))
                    if rooms:
                        list[building] = rooms.order_by("-important", "name")
        else:  # return all the buildings and rooms
            for building in Building.objects.order_by(
                "-room__important"
            ).distinct().order_by("name"):
                list[building] = building.room_set.order_by("-important", "name")
        context["list"] = list
        return context


class ListRoomView(TemplateView):
    template_name = "rooms/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all"] = False  # This flag will adapt the template
        # Create a dictionary where the keys are the buildings and the value is a queryset
        # with the rooms in the building
        list = OrderedDict([])
        # Check for filter-text
        # Search the text in the buildings and ain the rooms's name
        # (not in the description or address for now)
        if "search" in self.request.GET:
            text = self.request.GET.get("search", "")
            context["filterText"] = text
            for building in Building.objects.filter(room__important=True).order_by("name"):
                # if the text match with a building then return all the romms of the building
                if building.name.lower().find(text.lower()) != -1:
                    list[building] = building.room_set.filter(important=True).order_by(
                        "-important", "name"
                    )
                else:  # return only the rooms that have the text in the name
                    rooms = building.room_set.filter(important=True).filter(Q(name__icontains=text))
                    if rooms:
                        list[building] = rooms.order_by("-important", "name")
        else:  # if there is no search return all the importants rooms and buildings
            for building in Building.objects.filter(room__important=True).order_by("name"):
                list[building] = building.room_set.filter(important=True).order_by("name")
        context["list"] = list
        return context


class EditRoomView(TemplateView):
    template_name = "rooms/edit.html"

    permission_required = "rooms.change_room"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This key is needed for using google maps api
        context["API_KEY"] = GOOGLE_MAPS_API_KEY
        # This flag will allow to edit roomrules only who has the permission
        CAN_CHANGE_RULES = self.request.user.has_perm("roomRule.change_roomRule")
        context["changeRoomRules"] = CAN_CHANGE_RULES

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
        # If there is the building info in the session it means we are back from creating a building
        if ("roomForm_data" in self.request.session) and\
                self.request.session["roomForm_data"]["building"]:
            # Update the initial values of the form
            roomForm.initial = self.request.session.pop("roomForm_data")
        context["roomForm"] = roomForm
        if CAN_CHANGE_RULES:
            context["roomRuleForm"] = roomRuleForms
        return context

    def post(self, request, *args, **kwargs):

        CAN_CHANGE_RULES = self.request.user.has_perm("roomRule.change_roomRule")

        if "room_id" in kwargs and kwargs["room_id"]:
            try:
                room = Room.objects.get(pk=kwargs["room_id"])
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

        # Clear the session before so if we put new data they will be clear
        request.session.clear()

        # If the button create new building is pressed
        if request.POST.get('newBuilding'):
            roomForm.is_valid()  # This will fill cleaed_data
            # If is valid filled name and descrition then save them and go to create new building
            # else also the next if will fail and will be displayed the errors
            # (fix the the first error displayed will be the missed building)
            if ("name" in roomForm.cleaned_data) and ("description" in roomForm.cleaned_data):
                request.session["pendingRoom"] = True
                form_content = roomForm.data
                request.session["roomForm_data"] = form_content

                if kwargs["edit"]:  # Save the pk of the room we are editing
                    request.session["room_pk"] = room.pk
                return HttpResponseRedirect(reverse("rooms:newBuilding"))

        if roomForm.is_valid() and (roomRuleForms.is_valid() or not CAN_CHANGE_RULES):
            if CAN_CHANGE_RULES:
                roomRuleForms.save()
            if kwargs["edit"]:
                room = roomForm.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(room).pk,
                    object_id=room.id,
                    object_repr=str(room),
                    action_flag=CHANGE
                )
            else:
                room = roomForm.save(commit=False)
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


class NewRoomView(EditRoomView):
    permission_required = "room.create_room"


class EditBuildingView(TemplateView):
    template_name = "rooms/editBuilding.html"

    permission_required = "building.change_building"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Put in the context if we have a pending editing/creation a room
        if "pendingRoom"in self.request.session and self.request.session["pendingRoom"]:
            self.request.session["pendingRoom"] = False
            context["pendingRoom"] = "roomForm_data" in self.request.session
            context["editPendingRoom"] = "room_pk" in self.request.session
        if self.request.method == "GET":
            if "building_id" in kwargs and kwargs["building_id"]:
                try:
                    building = Building.objects.get(pk=kwargs["building_id"])
                except:
                    raise Http404
                buildingForm = BuildingForm(instance=building)
                context["edit"] = True
            else:
                buildingForm = BuildingForm()
        elif self.request.method == "POST":
            if "building_id" in kwargs and kwargs["building_id"]:
                try:
                    building = Building.objects.all().get(pk=kwargs["building_id"])
                except:
                    raise Http404
                buildingForm = BuildingForm(self.request.POST, instance=building)
            else:
                buildingForm = BuildingForm(self.request.POST)
            context["edit"] = kwargs["edit"]
        else:
            raise Http404
        context["buildingForm"] = buildingForm
        return context

    def post(self, request, *args, **kwargs):
        if "building_id" in kwargs and kwargs["building_id"]:
            try:
                building = Building.objects.get(pk=kwargs["building_id"])
            except:
                raise Http404
            buildingForm = BuildingForm(request.POST, instance=building)
            kwargs["edit"] = True
        else:
            buildingForm = BuildingForm(request.POST)
            kwargs["edit"] = False

        if buildingForm.is_valid():
            if kwargs["edit"]:
                building = buildingForm.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(building).pk,
                    object_id=building.id,
                    object_repr=str(building),
                    action_flag=CHANGE
                )
            else:
                building = buildingForm.save(commit=False)
                building.creator = request.user
                building.save()
                LogEntry.objects.log_action(
                    user_id=self.request.user.id,
                    content_type_id=ContentType.objects.get_for_model(building).pk,
                    object_id=building.id,
                    object_repr=str(building),
                    action_flag=ADDITION
                )
            # Check if we have a pending editing/creation of a room
            if "roomForm_data" in request.session:
                # Add the building to the room form data (that will be set as default)
                roomFormData = request.session["roomForm_data"].copy()
                roomFormData["building"] = building.pk
                request.session["roomForm_data"] = roomFormData
                # If the room pk has been saved then return to modify the room...
                if "room_pk" in request.session:
                    room_pk = request.session.pop("room_pk")
                    return HttpResponseRedirect(reverse(
                        "rooms:editRoom", kwargs={'room_id': room_pk})
                    )
                else:  # ...go back to create a new room
                    return HttpResponseRedirect(reverse("rooms:newRoom"))
            return HttpResponseRedirect(reverse("rooms:listall"))
        else:
            return self.get(request, *args, **kwargs)


class NewBuildingView(EditBuildingView):

    permission_required = "building.create_building"
