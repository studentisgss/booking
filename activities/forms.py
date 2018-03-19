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
            "brochure",
            "description",
            "managers",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow only active user with the permission (at user or group level) to change events
        perm = Permission.objects.get(codename='add_event')
        self.fields['managers'].queryset = User.objects.all().filter(
            is_active=True
        ).filter(
            Q(groups__permissions=perm) | Q(user_permissions=perm)
        ).distinct().order_by("first_name", "last_name")
        # Use the full name for the users
        self.fields['managers'].label_from_instance = self.managers_label_from_instance

    def managers_label_from_instance(self, obj):
        return obj.get_full_name()

    def clean_description(self):
        # Remove default lines in description__icontains
        spl_descr = Activity.DESCRIPTION_TEMPLATE.split("\n")
        act_descr = self.cleaned_data["description"]
        for spl_str in spl_descr:
                if len(spl_str.strip()) > 0:
                    act_descr = act_descr.replace(spl_str.strip(),'')
        return act_descr.rstrip()
