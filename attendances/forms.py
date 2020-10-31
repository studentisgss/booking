from base.forms import BookingModelForm, BookingForm
from attendances.models import GalileianAttendance, ForeignAttendance, Details


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
