from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rooms.models import Room, RoomRule
from base.utils import default_datetime


class RoomsDetailsUrlTest(TestCase):
    def test_invalid_ids(self):
        ids = ["0", "-1", "999999985751"]
        for room_id in ids:
            response = self.client.get("/rooms/detail/" + room_id)
            self.assertEqual(response.status_code, 404)

    def test_ids(self):
        ids = ["1", "2", "3", "4", "5"]
        for room_id in ids:
            response = self.client.get("/rooms/detail/" + room_id)
            # Check that status code is valid
            self.assertIn(response.status_code, (200, 404))


class RoomRuleCleanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test")
        self.room = Room.objects.create(name="Room 1", description="", creator=self.user)
        self.room2 = Room.objects.create(name="Room 2", description="", creator=self.user)
        RoomRule.objects.create(
            room=self.room,
            day=0,
            opening_time=default_datetime(2016, 5, 2, 8, 0).timetz(),
            closing_time=default_datetime(2016, 5, 2, 18, 0).timetz()
        )

    def test_opening_after_closing_rules_rejected(self):
        """ Test that rules with opening time greater than clsing time are rejected """
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room2,
                day=1,
                opening_time=default_datetime(2016, 5, 3, 16, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 14, 0).timetz()
            )
            rule.clean()

    def test_overlapping_rules_rejected(self):
        """ Test that overlapping rules are rejected """
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room,
                day=0,
                opening_time=default_datetime(2016, 5, 2, 9, 0).timetz(),
                closing_time=default_datetime(2016, 5, 2, 15, 0).timetz()
            )
            rule.clean()

    def test_valid_rules_accepted(self):
        """ Test that valid rules are not rejected """
        # Overlapping with a rule for a different room and with the same day
        try:
            rule = RoomRule(
                room=self.room2,
                day=0,
                opening_time=default_datetime(2016, 5, 3, 8, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 18, 0).timetz()
            )
            rule.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with overlapping rule for different room")

        # Overlapping with a rule with a different day and for the same room
        try:
            rule = RoomRule(
                room=self.room,
                day=1,
                opening_time=default_datetime(2016, 5, 3, 8, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 18, 0).timetz()
            )
            rule.clean()
        except ValidationError:
            self.fail(
                "ValidationError exception raised with overlapping rule for different day"
            )

        # Not overlapping at all
        try:
            rule = RoomRule(
                room=self.room2,
                day=1,
                opening_time=default_datetime(2016, 5, 3, 8, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 18, 0).timetz()
            )
            rule.clean()
        except ValidationError:
            self.fail("ValidationError exception raised with not overlapping rule")

    def test_none_day_rejected(self):
        """ Test that none day are rejected """
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room,
                day=None,
                opening_time=default_datetime(2016, 5, 3, 16, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 14, 0).timetz()
            )
            rule.clean()

    def test_none_room_rejected(self):
        """ Test that none room are rejected """
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=None,
                day=0,
                opening_time=default_datetime(2016, 5, 3, 16, 0).timetz(),
                closing_time=default_datetime(2016, 5, 3, 14, 0).timetz()
            )
            rule.clean()

    def test_none_time_rejected(self):
        """ Test that none time are rejected """
        # None opening_time
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room,
                day=0,
                opening_time=None,
                closing_time=default_datetime(2016, 5, 3, 14, 0).timetz()
            )
            rule.clean()
        # None closing_time
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room,
                day=0,
                opening_time=default_datetime(2016, 5, 3, 16, 0).timetz(),
                closing_time=None
            )
            rule.clean()
        # None both opening_time and closing_time
        with self.assertRaises(ValidationError):
            rule = RoomRule(
                room=self.room,
                day=0,
                opening_time=None,
                closing_time=None
            )
            rule.clean()
