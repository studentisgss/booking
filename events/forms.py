from base.forms import BookingModelForm
from django.forms import modelformset_factory, inlineformset_factory, BaseModelFormSet
from django.forms.fields import SplitDateTimeField
from events.models import Event
from activities.models import Activity


class EventForm(BookingModelForm):
    class Meta:
        model = Event
        fields = [
            "room",
            "start",
            "end",
        ]
        field_classes = {
            "start": SplitDateTimeField,
            "end": SplitDateTimeField,
        }

    start = SplitDateTimeField(
        input_date_formats=("%d/%m/%Y",),
        input_time_formats=("%H:%M:%S",),
    )


EventInlineFormSet = inlineformset_factory(Activity, Event, fields=(
    "room",
    "start",
    "end",
), form=EventForm)
