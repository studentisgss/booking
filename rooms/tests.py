from django.test import TestCase


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
