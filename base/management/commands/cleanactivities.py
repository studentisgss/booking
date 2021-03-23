from django.core.management.base import BaseCommand, CommandError
from activities.models import Activity


class Command(BaseCommand):
    help = 'Clean the activities, removing them all from brochure and archiving them all'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Activity.objects.all().update(
            archived = True,
            brochure = False
        )