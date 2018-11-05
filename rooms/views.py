from collections import OrderedDict

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from booking.settings import GOOGLE_MAPS_API_KEY
from rooms.models import Group, Room, Building, RoomRule, RoomPermission
from rooms.forms import RoomForm, BuildingForm, RoomRuleInlineFormSet, \
    RoomPermissionInlineFormSet, RoomRuleForm, RoomPermissionForm, get_default_permissions


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
        context["can_require"] = Group.objects.filter(
            roompermission__room=room, roompermission__permission=10)
        context["can_book"] = Group.objects.filter(
            roompermission__room=room, roompermission__permission=30)
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


class EditRoomView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "rooms/edit.html"

    permission_required = "rooms.change_room"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This key is needed for using google maps api
        context["API_KEY"] = GOOGLE_MAPS_API_KEY
        # This flag will allow to edit roomrules only who has the permission
        CAN_CHANGE_RULES = self.request.user.has_perm("rooms.change_roomrule") \
            and self.request.user.has_perm("rooms.add_roomrule")
        CAN_CHANGE_PERMISSIONS = self.request.user.has_perm("rooms.change_roompermission") \
            and self.request.user.has_perm("rooms.add_roompermission")

        roomRuleForms_max_num = Group.objects.all().count()

        if self.request.method == "GET":
            if "room_id" in kwargs and kwargs["room_id"]:
                try:
                    room = Room.objects.all().get(pk=kwargs["room_id"])
                except:
                    raise Http404
                roomForm = RoomForm(instance=room)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(instance=room)
                if CAN_CHANGE_PERMISSIONS:
                    RoomPermissionForms = RoomPermissionInlineFormSet(instance=room)
                    RoomPermissionForms.max_num = roomRuleForms_max_num
                context["edit"] = True
            else:
                roomForm = RoomForm()
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet()
                if CAN_CHANGE_PERMISSIONS:
                    RoomPermissionForms = RoomPermissionInlineFormSet(
                        initial=get_default_permissions())
                    RoomPermissionForms.max_num = roomRuleForms_max_num
        elif self.request.method == "POST":
            if "room_id" in kwargs and kwargs["room_id"]:
                try:
                    room = Room.objects.all().get(pk=kwargs["room_id"])
                except:
                    raise Http404
                roomForm = RoomForm(self.request.POST, instance=room)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(self.request.POST, instance=room)
                if CAN_CHANGE_PERMISSIONS:
                    RoomPermissionForms = RoomPermissionInlineFormSet(self.request.POST, instance=room)
                    RoomPermissionForms.max_num = roomRuleForms_max_num
            else:
                roomForm = RoomForm(self.request.POST)
                if CAN_CHANGE_RULES:
                    roomRuleForms = RoomRuleInlineFormSet(self.request.POST)
                if CAN_CHANGE_PERMISSIONS:
                    RoomPermissionForms = RoomPermissionInlineFormSet(self.request.POST)
                    RoomPermissionForms.max_num = roomRuleForms_max_num
            context["edit"] = kwargs["edit"]
        else:
            raise Http404
        # If there is the building info in the session it means we are back from creating a building
        if ("roomForm_data" in self.request.session) and\
                "building" in self.request.session["roomForm_data"]:
            # Update the initial values of the form
            roomForm.initial = self.request.session.pop("roomForm_data")
        context["roomForm"] = roomForm
        if CAN_CHANGE_RULES:
            context["roomRuleForm"] = roomRuleForms
        if CAN_CHANGE_PERMISSIONS:
            context["RoomPermissionForm"] = RoomPermissionForms
        return context

    def post(self, request, *args, **kwargs):

        CAN_CHANGE_RULES = self.request.user.has_perm("rooms.change_roomrule")
        CAN_CHANGE_PERMISSIONS = self.request.user.has_perm("rooms.change_roompermission")

        if "room_id" in kwargs and kwargs["room_id"]:  # editing room
            try:
                room = Room.objects.get(pk=kwargs["room_id"])
            except:
                raise Http404
            roomForm = RoomForm(request.POST, instance=room)
            if CAN_CHANGE_RULES:
                roomRuleForms = RoomRuleInlineFormSet(request.POST, instance=room)
            if CAN_CHANGE_PERMISSIONS:
                RoomPermissionForms = RoomPermissionInlineFormSet(request.POST, instance=room)
            kwargs["edit"] = True
        else:  # creating new room
            roomForm = RoomForm(request.POST)
            if CAN_CHANGE_RULES:
                roomRuleForms = RoomRuleInlineFormSet(request.POST)
            if CAN_CHANGE_PERMISSIONS:
                RoomPermissionForms = RoomPermissionInlineFormSet(request.POST)
            kwargs["edit"] = False

        # Clear the session before put new data into
        if "pendingRoom" in request.session:
            del request.session["pendingRoom"]
        if "roomForm_data" in request.session:
            del request.session["roomForm_data"]
        if "room_pk" in request.session:
            del request.session["room_pk"]

        # If the button create new building is pressed
        if request.POST.get('newBuilding') and self.request.user.has_perm("rooms.add_building"):
            roomForm.is_valid()  # This will fill cleaed_data
            # If is valid filled name and descrition then save them and go to create new building
            # else also the next if will fail and will be displayed the errors
            # (fix the the first error displayed will be the missed building)
            if ("name" in roomForm.cleaned_data) and ("description" in roomForm.cleaned_data):
                request.session["pendingRoom"] = True
                form_content = roomForm.data.copy()
                del form_content["building"]
                request.session["roomForm_data"] = form_content
                if kwargs["edit"]:  # Save the pk of the room we are editing
                    request.session["room_pk"] = room.pk
                return HttpResponseRedirect(reverse("rooms:newBuilding"))

        if roomForm.is_valid() and (not CAN_CHANGE_RULES or roomRuleForms.is_valid()) and \
                (not CAN_CHANGE_PERMISSIONS or RoomPermissionForms.is_valid()):
            if not self.request.user.has_perm("rooms.can_change_important"):
                if "important" in roomForm.changed_data:
                    raise PermissionDenied
            if kwargs["edit"]:
                if CAN_CHANGE_RULES:
                    roomRuleForms.save()
                if CAN_CHANGE_PERMISSIONS:
                    RoomPermissionForms.save()
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
                if CAN_CHANGE_RULES:
                    roomRules = roomRuleForms.save(commit=False)
                    for rule in roomRules:
                        rule.room = room
                        rule.save()
                if CAN_CHANGE_PERMISSIONS:
                    roomPermissions = RoomPermissionForms.save(commit=False)
                    for permission in roomPermissions:
                        permission.room = room
                        permission.save()
                else:
                    # create the RoomPermissions as deafault
                    room.create_roompermission()
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

    permission_required = "rooms.add_room"


class EditBuildingView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "rooms/editBuilding.html"

    permission_required = "rooms.change_building"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This key is needed for using google maps api
        context["API_KEY"] = GOOGLE_MAPS_API_KEY
        # Put in the context if we have a pending editing/creation a room
        if "pendingRoom" in self.request.session and self.request.session["pendingRoom"]:
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
            if request.POST.get('pendingRoom'):
                # Add the building to the room form data (that will be set as default)
                roomFormData = request.session["roomForm_data"]
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

    permission_required = "rooms.add_building"
