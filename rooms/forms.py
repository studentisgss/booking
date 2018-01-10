from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError

from base.forms import BookingModelForm
from rooms.models import Room, RoomRule
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
        ]

    # Since is_valid don't check if the building field is not none,
    # this method return true only if the room form is well filled (compatible with the model)
    def is_almost_clean(self):
        return super().clean()

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


class BaseRoomRuleInlineFormSet(BaseInlineFormSet):

    def get_queryset(self):
        return super().get_queryset().order_by("day")


# create a set of forms for the RoomRules on several days
RoomRuleInlineFormSet = inlineformset_factory(
    Room, RoomRule, form=RoomRuleForm, formset=BaseRoomRuleInlineFormSet, extra=5, max_num=7
)
