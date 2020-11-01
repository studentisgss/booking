from base.forms import BookingModelForm, BookingForm
from attendances.models import GalileianAttendance, ForeignAttendance, Details
from django.forms import DateField, DateInput
from booking import settings
import datetime

class GalileianAttendanceForm(BookingModelForm):
    class Meta:
        model = GalileianAttendance
        fields = [
            "event",
            "chair"
        ]


class ForeignAttendanceForm(BookingModelForm):
    class Meta:
        model = ForeignAttendance
        fields = [
            "event",
            "chair",
            "first_name",
            "last_name",
            "cell_number",
            "matricola",
            "email"
        ]


class DetailsForm(BookingModelForm):
    class Meta:
        model = Details
        fields = [
            "cell_number",
            "matricola"
        ]

class ExtractPeriodForm(BookingForm):
    start_date = DateField(label='Da',
                           initial=datetime.date.today)
    end_date = DateField(label='A',
                         initial=datetime.date.today)