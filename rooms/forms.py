from base.forms import BookingModelForm
from rooms.models import Room
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

#class RoomRuleInlineFormSet(BaseInlineFormSet):



#RoomRulesInlineFormSet = inlineformset_factory(Room, Building, fields=(
#    "opening",
#    "end",
#    "status",
#), form=EventForm, formset=BaseEventInlineFormset, extra=2)
