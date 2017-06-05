from base.forms import BookingModelForm
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.forms.fields import SplitDateTimeField
from django.forms.widgets import SplitDateTimeWidget
from django.core.exceptions import ValidationError

from events.models import Event
from activities.models import Activity
from booking import settings


class EventForm(BookingModelForm):
    class Meta:
        model = Event
        fields = [
            "room",
            "start",
            "end",
            "status",
        ]
        field_classes = {
            "start": SplitDateTimeField,
            "end": SplitDateTimeField,
        }

    start = SplitDateTimeField(
        input_date_formats=("%d/%m/%Y",),
        input_time_formats=("%H:%M", "%H:%M:%S",),
        widget=SplitDateTimeWidget(
            date_format=settings.DATE_FORMAT,
            time_format=settings.TIME_FORMAT
        )
    )

    end = start = SplitDateTimeField(
        input_date_formats=("%d/%m/%Y",),
        input_time_formats=("%H:%M", "%H:%M:%S",),
        widget=SplitDateTimeWidget(
            date_format=settings.DATE_FORMAT,
            time_format=settings.TIME_FORMAT
        )
    )


class BaseEventInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        instances = []
        for form in self.forms:
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

    def get_queryset(self):
        return super().get_queryset().order_by("start")


EventInlineFormSet = inlineformset_factory(Activity, Event, fields=(
    "room",
    "start",
    "end",
    "status",
), form=EventForm, formset=BaseEventInlineFormset, extra=2)
