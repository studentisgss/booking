from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.


class Place(models.Model):
    """
    Luoghi nei quali si potranno tenere gli eventi,
    innanzitutto le aule galileo, l'aula magna ecc...
    Si potranno poi aggiungere luoghi esterni dove verrano tenuti i corsi.
    Quelli contrassegnati da "important" saranno le aule
    che verranno evidenziate del software.
    ---
    Places where events will take place,
    firstable galileo rooms, aula magna and so on...
    "important"-tagged rooms will be highlighted by the software.
    """
    class Meta:
        permissions = (
            ("can_book_place", "Can book some place"),
        )

    def __str__(self):
        return "%s %s" % ("*" if self.important else "", self.name)

    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    important = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="place_created")

    def get_group_perm(group):
        if group.has_perm("booking.can_book_place"):
            return PlacePermisson.objects.get(place=self,
                                              group=group).permission
        return 0

    def show_request_to_group(group):
        return PlacePermisson.objects.get(place=self, group=group).showrequest


class PlacePermisson(models.Model):
    """
    Permessi per ogni aula/luogo ed ogni gruppo
    Ad ogni aula ed ogni gruppo e' associato un livello di permesso
    e se le richieste per quest'aula vengono evidenziate/mostrate
    per gli utenti del gruppo
    ---
    Permissions for every room/place and every group
    Per every room and every group is associated a level of permissions
    and if requests of this room are highlighted/shown for users of the group.
    """
    def __str__(self):
        return "Place%d & Group%d" % (self.place_id, self.group_id)

    PERM_LEVEL = [
        (10, "Puo' richiedere"),
        (30, "Puo' approvare"),
    ]
    place = models.ForeignKey(Place)
    group = models.ForeignKey(Group)
    permission = models.SmallIntegerField(choices=PERM_LEVEL, default=10)
