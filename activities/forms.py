from base.forms import BookingModelForm
from activities.models import Activity


class ActivityForm(BookingModelForm):
    class Meta:
        model = Activity
        fields = [
            "category",
            "title",
            "professor",
            "archived",
            "description",
        ]
