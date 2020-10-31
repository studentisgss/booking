from base.forms import BookingModelForm
from attendances.models import GalileianAttendance, ForeignAttendance, Phone

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
            "email"
        ]

class PhoneForm(BookingModelForm):
    class Meta:
        model = Phone
        fields = [
            "cell_number"
        ]