from django.test import TestCase
from django.core.exceptions import ValidationError
from base.views import GenericTemplateView
from base.utils import default_datetime
from rooms.models import Room
from django.contrib.auth.models import User
from activities.models import Activity
from events.models import Event
from bs4 import BeautifulSoup


class EventsCleanTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@dev.dev", password="test")
        self.room = Room.objects.create(name="Room1", description="", creator=self.user)
        self.activity = Activity.objects.create(
            title="Activity1",
            description="",
            creator=self.user
        )
        event = Event.objects.create(
            room=self.room,
            activity=self.activity,
            status=0,
            start=default_datetime(2016, 5, 3, 14, 0),
            end=default_datetime(2016, 5, 3, 16, 0),
            creator=self.user
        )

    def test_start_after_end_raises_exception(self):
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=0,
                start=default_datetime(2016, 5, 3, 19, 0),
                end=default_datetime(2016, 5, 3, 17, 0),
                creator=self.user
            )
            event.clean()

    def test_different_day_raises_exception(self):
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=0,
                start=default_datetime(2016, 5, 3, 17, 0),
                end=default_datetime(2016, 5, 4, 19, 0),
                creator=self.user
            )
            event.clean()

    # TODO
    # - Check third condition in clean()
    # - Check clean() success
