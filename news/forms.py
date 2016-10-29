from django.forms import ModelForm, Textarea
from news.models import News


class NewsForm(ModelForm):
    class Meta:
        model = News
        fiels = [
            "title",
            "content",
            "start",
            "end",
        ]
