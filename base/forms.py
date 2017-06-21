from django.forms import ModelForm, widgets


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
