from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.


class Room(models.Model):
    """
    Rooms where events will take place,
    firstable galileo rooms, aula magna and so on...
    Others rooms can be added later.
    "important"-tagged rooms will be highlighted by the software.
    """
    class Meta:
        permissions = (
            ("can_book_room", "Can book some room"),
        )

    def __str__(self):
        return "%s %s" % ("*" if self.important else "", self.name)

    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    important = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="room_created", on_delete=models.CASCADE)

    def get_group_perm(group):
        if group.has_perm("booking.can_book_room"):
            return RoomPermisson.objects.get(
                room=self,
                group=group
            ).permission
        return 0

    def show_request_to_group(group):
        return RoomPermisson.objects.get(room=self, group=group).showrequest


class RoomPermisson(models.Model):
    """
    Permissions for every room and every group.
    To every room and every group is associated a level of permissions
    and if requests of this room are highlighted/shown for users of the group.
    """
    def __str__(self):
        return "Room%d & Group%d" % (self.room_id, self.group_id)

    PERMISSION_CHOICES = [
        (10, "Can request"),
        (30, "Can accept"),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission = models.SmallIntegerField(
        choices=PERMISSION_CHOICES,
        default=10
    )
