from base.forms import BookingModelForm
from news.models import News, Message


class NewsForm(BookingModelForm):
    class Meta:
        model = News
        fields = [
            "title",
            "content",
            "start",
            "end",
        ]


class MessageForm(BookingModelForm):
    class Meta:
        model = Message
        fields = ["title", "content"]
