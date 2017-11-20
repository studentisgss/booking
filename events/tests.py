from django.test import TestCase
from django.core.exceptions import ValidationError
from base.utils import default_datetime
from rooms.models import Room, RoomRule
from django.contrib.auth.models import User
from activities.models import Activity
from events.models import Event


class EventsCleanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test")
        self.room = Room.objects.create(name="Room 1", description="", creator=self.user)
        self.room2 = Room.objects.create(name="Room 2", description="", creator=self.user)
        self.room3 = Room.objects.create(name="Room 3", description="", creator=self.user)
        self.activity = Activity.objects.create(
            title="Activity 1",
            description="",
            creator=self.user
        )
        Event.objects.create(
            room=self.room,
            activity=self.activity,
            status=Event.APPROVED,
            start=default_datetime(2016, 5, 3, 14, 0),
            end=default_datetime(2016, 5, 3, 16, 0),
            creator=self.user
        )
        Event.objects.create(
            room=self.room,
            activity=self.activity,
            status=Event.REJECTED,
            start=default_datetime(2016, 5, 2, 14, 0),
            end=default_datetime(2016, 5, 2, 16, 0),
            creator=self.user
        )
        RoomRule.objects.create(
            room=self.room3,
            day=0,
            opening_time=default_datetime(2016, 5, 2, 8, 0).timetz(),
            closing_time=default_datetime(2016, 5, 2, 18, 0).timetz()
        )

    def test_start_after_end_events_rejected(self):
        """ Test that events with start time greater than end time are rejected """
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

    def test_different_day_events_rejected(self):
        """ Test that events with start and end time in different days are rejected """
        # Event longer than 24 hours
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

        # Event shorter than 24 hours
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 1, 23, 0),
                end=default_datetime(2016, 5, 2, 1, 0),
                creator=self.user
            )
            event.clean()

    def test_approved_overlapping_events_rejected(self):
        """ Test that approved overlapping events are rejected """
        # Overlapping by 1 minute at the end
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 12, 0),
                end=default_datetime(2016, 5, 3, 14, 1),
                creator=self.user
            )
            event.clean()

        # Overlapping by 1 minute at the beginning
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 15, 59),
                end=default_datetime(2016, 5, 3, 17, 0),
                creator=self.user
            )
            event.clean()

        # Completely overlapping, "contained" in another event
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 15, 00),
                end=default_datetime(2016, 5, 3, 15, 30),
                creator=self.user
            )
            event.clean()

        # Completely overlapping, "containing" another event
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 12, 00),
                end=default_datetime(2016, 5, 3, 18, 00),
                creator=self.user
            )
            event.clean()

    def test_waiting_overlapping_events_rejected(self):
        """ Test that waiting overlapping events are rejected """
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.WAITING,
                start=default_datetime(2016, 5, 3, 12, 00),
                end=default_datetime(2016, 5, 3, 16, 00),
                creator=self.user
            )
            event.clean()

    def test_valid_events_accepted(self):
        """ Test that valid events are not rejected """
        # A rejected overlapping event is ok
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

        # Overlapping with an event in a different room and with the same activity
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

        # An approved event overlapping with a rejected event
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

        # Not overlapping, but immediately before another event
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

        # Not overlapping, but immediately after another event
        try:
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 3, 16, 0),
                end=default_datetime(2016, 5, 3, 18, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping event")

    def test_none_date_rejected(self):
        """ Test that none dates are rejected """
        # Start date is none
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.REJECTED,
                start=None,
                end=default_datetime(2016, 5, 3, 12, 0),
                creator=self.user
            )
            event.clean()

        # End date is none
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.REJECTED,
                start=default_datetime(2016, 5, 3, 16, 0),
                end=None,
                creator=self.user
            )
            event.clean()

        # Both dates are none
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room,
                activity=self.activity,
                status=Event.REJECTED,
                start=None,
                end=None,
                creator=self.user
            )
            event.clean()

    def test_none_room_rejected(self):
        """ Test that none room are rejected """
        User.objects.create_superuser("dev", "dev@test.com", "dev")
        self.client.login(username="dev", password="dev")
        response = self.client.post("/admin/events/event/add/", {
            "room": None,
            "activity": 13,
            "start_0": "11/10/2016",
            "start_1": "18:52:33",
            "end_0": "11/10/2016",
            "end_1": "18:57:34",
            "status": 0,
            "creator": 1,
            "_save": "Salva"
        })
        self.assertEqual(response.status_code, 200)

    def test_events_when_room_closed_rejected(self):
        """ Test that events with start before opening time
        or end after closing time are rejected """
        # Start before opening time
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room3,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 7, 59),
                end=default_datetime(2016, 5, 2, 17, 0),
                creator=self.user
            )
            event.clean()
        # End after closing time
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room3,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 9, 0),
                end=default_datetime(2016, 5, 2, 18, 1),
                creator=self.user
            )
            event.clean()
        # Start before opening time and end after clofing time
        with self.assertRaises(ValidationError):
            event = Event(
                room=self.room3,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 6, 0),
                end=default_datetime(2016, 5, 2, 19, 0),
                creator=self.user
            )
            event.clean()

    def test_events_when_room_open_accepted(self):
        """Test that events within the opening hours are not rejected"""
        # General event
        try:
            event = Event(
                room=self.room3,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 14, 0),
                end=default_datetime(2016, 5, 2, 16, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping event")
        # All day long event
        try:
            event = Event(
                room=self.room3,
                activity=self.activity,
                status=Event.APPROVED,
                start=default_datetime(2016, 5, 2, 8, 0),
                end=default_datetime(2016, 5, 2, 18, 0),
                creator=self.user
            )
            event.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping event")
