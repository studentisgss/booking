from base.forms import BookingModelForm
from django.forms import inlineformset_factory, BaseInlineFormSet, ModelChoiceField
from django.forms.fields import SplitDateTimeField, ChoiceField
from django.forms.widgets import SplitDateTimeWidget
from django.core.exceptions import ValidationError

from events.models import Event
from rooms.models import Room
from activities.models import Activity
from booking import settings


# This field will rappresent the relationship between rooms and buildings
class RoomChoiceField(ModelChoiceField):
    def __init__(self, *args, **kwargs):
        # kwargs['required'] = False
        super(RoomChoiceField, self).__init__(*args, **kwargs)


class RooOrOnlinChoiceField(ChoiceField):
    def validate(self, value):  # No validation needed: field Room and Online validates by itself
        pass


class EventForm(BookingModelForm):
    class Meta:
        model = Event
        fields = [
            "room",
            "online",
            "start",
            "end",
            "status",
            "exam"
        ]
        field_classes = {
            "room": RoomChoiceField,
            "start": SplitDateTimeField,
            "end": SplitDateTimeField
        }

    start = SplitDateTimeField(
        input_date_formats=settings.DATE_INPUT_FORMATS,
        input_time_formats=settings.TIME_INPUT_FORMATS,
        widget=SplitDateTimeWidget(
            date_format=settings.DATE_FORMAT,
            time_format=settings.TIME_FORMAT
        )
    )

    end = start = SplitDateTimeField(
        input_date_formats=settings.DATE_INPUT_FORMATS,
        input_time_formats=settings.TIME_INPUT_FORMATS,
        widget=SplitDateTimeWidget(
            date_format=settings.DATE_FORMAT,
            time_format=settings.TIME_FORMAT
        )
    )

    roo_or_onlin = RooOrOnlinChoiceField()
    # it should be room_or_online, but to prevent confusion with room and online the last letters are removed


class BaseEventInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseEventInlineFormset, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        instances = []
        for form in self.forms:
            try:
                if (form.instance.end and
                        form.instance.start and
                        form.instance.room and
                        form.instance.status is not None):
                    for i in instances:
                        if (form.instance.status != Event.REJECTED and
                                i.start < form.instance.end and
                                i.end > form.instance.start and
                                i.room == form.instance.room):
                            e = ValidationError("Non si possono inserire due eventi non rifiutati"
                                                " sovrapposti per la stessa aula.")
                            form.add_error(None, e)

                    if form.instance.status != Event.REJECTED:
                        instances.append(form.instance)
            except Room.DoesNotExist:
                # If the room is not set then do nothing
                # as the form will fail Room.clean()
                pass

    def get_queryset(self):
        return super().get_queryset().order_by("start")


EventInlineFormSet = inlineformset_factory(Activity, Event, fields=(
    "room",
    "online",
    "roo_or_onlin",
    "start",
    "end",
    "status",
    "exam",
), form=EventForm, formset=BaseEventInlineFormset, extra=2)
