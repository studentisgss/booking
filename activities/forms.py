from base.forms import BookingModelForm
from activities.models import Activity

from django.contrib.auth.models import User, Permission
from django.db.models import Q


class ActivityForm(BookingModelForm):
    class Meta:
        model = Activity
        fields = [
            "category",
            "title",
            "professor",
            "archived",
            "description",
            "managers",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perm = Permission.objects.get(codename='add_event')
        self.fields['managers'].queryset = User.objects.all().filter(
            is_active=True
        ).filter(
            Q(groups__permissions=perm) | Q(user_permissions=perm)
        ).distinct()
        self.fields['managers'].label_from_instance = self.managers_label_from_instance

    def managers_label_from_instance(self, obj):
        return obj.get_full_name()
