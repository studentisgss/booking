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
        self.room2 = Room.objects.create(name="Room2", description="", creator=self.user)
        self.activity = Activity.objects.create(
            title="Activity1",
            description="",
            creator=self.user
        )
        event1 = Event.objects.create(
            room=self.room,
            activity=self.activity,
            status=Event.APPROVED,
            start=default_datetime(2016, 5, 3, 14, 0),
            end=default_datetime(2016, 5, 3, 16, 0),
            creator=self.user
        )
        event_rejected = Event.objects.create(
            room=self.room,
            activity=self.activity,
            status=Event.REJECTED,
            start=default_datetime(2016, 5, 2, 14, 0),
            end=default_datetime(2016, 5, 2, 16, 0),
            creator=self.user
        )

    def test_start_after_end_raises_exception(self):
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
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
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 17, 0),
                end=default_datetime(2016, 5, 4, 19, 0),
                creator=self.user
            )
            event.clean()

    def test_rejected_overlapping_event_success(self):
        try:
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.REJECTED,
                start=default_datetime(2016, 5, 3, 14, 0),
                end=default_datetime(2016, 5, 3, 16, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with rejected overlapping event")

    def test_overlapping_event_raises_exception(self):
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 13, 0),
                end=default_datetime(2016, 5, 3, 15, 0),
                creator=self.user
            )
            event.clean()

        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 15, 0),
                end=default_datetime(2016, 5, 3, 17, 0),
                creator=self.user
            )
            event.clean()

        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 15, 0),
                end=default_datetime(2016, 5, 3, 15, 30),
                creator=self.user
            )
            event.clean()

    def test_clean_success(self):
        # Overlapping event but different room
        try:
            event = Event(
                room=self.room2,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 14, 0),
                end=default_datetime(2016, 5, 3, 16, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with overlapping event in different room")

        # Overlapping event with rejected event
        try:
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 14, 0),
                end=default_datetime(2016, 5, 2, 16, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail(
                "ValidationError exception raised with event overlapping with a rejected event"
            )
        # Not overlapping event for same room
        try:
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 12, 0),
                end=default_datetime(2016, 5, 3, 14, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping event")
        try:
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 17, 0),
                end=default_datetime(2016, 5, 3, 19, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping event")
