from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models.deletion import Collector


class Command(BaseCommand):
    help = 'Clear the users removing those inactive and with no other elements that refers to them'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        deleted_users = 0
        for u in User.objects.filter(is_active=False):
            c = Collector(using="default")
            c.collect([u])
            if len(list(c.instances_with_model())) == 1:
                u.delete()
                deleted_users += 1
        self.stdout.write(
            self.style.SUCCESS("Deleted %d users." % (deleted_users))
        )
