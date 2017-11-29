from django.forms import inlineformset_factory, BaseInlineFormSet

from base.forms import BookingModelForm
from rooms.models import Room, RoomRule
from rooms.models import Building


class RoomForm(BookingModelForm):
    class Meta:
        model = Room
        fields = [
            "name",
            "description",
            "building",
        ]

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

class BaseRoomRuleInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()


RoomRuleInlineFormSet = inlineformset_factory(Room, RoomRule, form=RoomRuleForm, formset=BaseRoomRuleInlineFormSet, max_num=7)
