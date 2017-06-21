from base.forms import BookingModelForm
from news.models import News


class NewsForm(BookingModelForm):
    class Meta:
        model = News
        fields = [
            "title",
            "content",
            "start",
            "end",
        ]
