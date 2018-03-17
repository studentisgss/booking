from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission, Group

from base.forms import BookingModelForm
from rooms.models import Room, RoomRule, RoomPermission
from rooms.models import Building


class RoomForm(BookingModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["building"].required = False

    class Meta:
        model = Room
        fields = [
            "name",
            "description",
            "building",
            "important",
        ]

    def clean(self):
        super().clean()
        if not self.data["building"]:
            self.add_error(None, ValidationError("""Il campo edificio è obbligatorio.
            Selezionane uno o premi Crea nouvo edificio per crearne uno."""))


class BuildingForm(BookingModelForm):
    class Meta:
        model = Building
        fields = [
            "name",
            "address"
        ]


class RoomRuleForm(BookingModelForm):
    class Meta:
        model = RoomRule
        fields = [
            "day",
            "opening_time",
            "closing_time"
        ]


class RoomPermissionForm(BookingModelForm):
    class Meta:
        model = RoomPermission
        fields = [
            "group",
            "permission"
        ]


class BaseRoomRuleInlineFormSet(BaseInlineFormSet):

    def get_queryset(self):
        return super().get_queryset().order_by("day")


class BaseRoomPermissionInlineFormSet(BaseInlineFormSet):

    def get_queryset(self):
        return super().get_queryset().order_by("-permission")


# create a set of forms for the RoomRules on several days
RoomRuleInlineFormSet = inlineformset_factory(
    Room, RoomRule, form=RoomRuleForm, formset=BaseRoomRuleInlineFormSet, extra=5, max_num=7
)

# create a set of forms for the RoomPermission on different groups
RoomPermissionInlineFormSet = inlineformset_factory(
    Room, RoomPermission, form=RoomPermissionForm, formset=BaseRoomPermissionInlineFormSet,
    extra=100
)


def get_default_permissions():
    initial = []
    can_book_room_permission = Permission.objects.get(codename="can_book_room")
    for group in Group.objects.filter(permissions=can_book_room_permission):
        initial.append({"group": group, "permission": 30})
    for group in Group.objects.exclude(permissions=can_book_room_permission):
        initial.append({"group": group, "permission": 10})
    return initial
