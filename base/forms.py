from django.forms import Form, ModelForm, widgets
from django.contrib.auth.models import User
from django import forms


class BookingModelForm(ModelForm):
    """
    This class extend the ModelForm adding custom class for Bootstrap ("form-control")
    and for better handling of date and datetime input
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classes_to_use = "form-control"
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': classes_to_use})

            # If the widget is for a date the add class 'date'
            if isinstance(self.fields[field].widget, widgets.DateInput):
                self.fields[field].widget.attrs['class'] += " date"

            # If the widget is for a date and a time the add class 'datetime'
            if isinstance(self.fields[field].widget, widgets.DateTimeInput):
                self.fields[field].widget = widgets.SplitDateTimeWidget(
                    attrs=self.fields[field].widget.attrs,
                    date_format='%d/%m/%Y',
                    time_format='%H:%M',
                )
                self.fields[field].widget.attrs['class'] += " datetime"

            if isinstance(self.fields[field].widget, widgets.SplitDateTimeWidget):
                self.fields[field].widget.attrs['class'] += " datetime"


class BookingForm(Form):
    """
    This class extend the Form adding custom class for Bootstrap ("form-control")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classes_to_use = "form-control"
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': classes_to_use})


class UserFileForm(BookingForm):
    user_file = forms.FileField(allow_empty_file=False)


class GroupMembersForm(BookingForm):

    members = forms.ModelMultipleChoiceField(User.objects.none())

    def __init__(self, group, exclude=True, *args, **kwargs):
        """
        group: The group we are interested in
        exclude: if true only the user not in the group will be listed
                 otherwise only the user in the group.
        """
        super().__init__(*args, **kwargs)
        if exclude:
            queryset = User.objects.all().filter(is_active=True).exclude(
                groups=group
            ).distinct()
        else:
            queryset = group.user_set

        self.fields['members'].queryset = queryset.order_by("first_name", "last_name")
        # Use the full name for the users
        self.fields['members'].label_from_instance = self.members_label_from_instance

        # Set the prefix to avoid multiple ids
        self.prefix = "%s-%s" % ("add" if exclude else "rem", group.pk)

    def members_label_from_instance(self, obj):
        return obj.get_full_name()
