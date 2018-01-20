from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from events.models import Event
from django.db import transaction, IntegrityError
import argparse
import csv


class Command(BaseCommand):
    help = '''Update the users based on a csv file which contains the list of the active users.
    The csv file must be without heading and with the fields: username, email, first_name, surname.
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-preserve-superusers',
            action='store_false',
            dest='preserve_superusers',
            help='Check also the superusers',
        )
        parser.add_argument('file', type=argparse.FileType('r'), help="Csv file")

    def handle(self, *args, **options):
        # Variables used
        active_users = User.objects.all().filter(is_active=True)
        if options["preserve_superusers"]:
            active_users = active_users.filter(is_superuser=False)
        else:
            self.stdout.write(
                self.style.WARNING("Also the superusers will be deactivated if not in the file.")
            )
        csv_users = {}
        deactivated_users_count = 0
        added_users_count = 0

        # Load the csv file into a dictionary: the key are the usernames and the value is another
        # dictionary with the first name and surname
        reader = csv.DictReader(options["file"],
                                fieldnames=("username", "email", "first_name", "surname"))
        for row in reader:
            uname = row["username"]
            if uname in csv_users:
                # ERROR: Duplicated username
                raise CommandError("Duplicated usernames in the csv file")
            csv_users[uname] = {"first_name": row["first_name"],
                                "surname": row["surname"],
                                "email": row["email"]}

        # Commit only if all is OK
        with transaction.atomic():
            # Check the active users
            self.stdout.write("Checking the active users...")
            for u in active_users:
                if u.username in csv_users:
                    del csv_users[u.username]  # Remove the user from the list
                else:
                    u.is_active = False
                    u.is_staff = False
                    u.is_superuser = False
                    u.save()
                    deactivated_users_count += 1
            # Remove the active superuser from the list
            for u in User.objects.filter(is_active=True, is_superuser=True):
                if u.username in csv_users:
                    del csv_users[u.username]
            # Add the new users
            self.stdout.write("Adding the new users...")
            for u, name in csv_users.items():
                user = None
                if not User.objects.filter(username=u).exists():
                    user = User.objects.create_user(u, name["email"])
                    user.first_name = name["first_name"]
                    user.last_name = name["surname"]
                else:
                    user = User.objects.get(username=u)
                    # If the user has different a different name raise an exception
                    if (user.first_name != name["first_name"]) or \
                            (user.last_name != name["surname"]) or \
                            (user.email != name["email"]):
                        raise CommandError(
                            "Usernames %s already in the database but with different name" % u
                        )
                    # Else reactivate him
                    user.is_active = True
                    c = ContentType.objects.get_for_model(Event)
                    perms = Permission.objects.filter(content_type=c)
                    user.user_permissions.add(*perms)
                user.save()
                added_users_count += 1

        # All the user have been updated succesfully
        self.stdout.write(self.style.SUCCESS("All the users have been updated."))
        self.stdout.write("Deactivated users: %d" % deactivated_users_count)
        self.stdout.write("Added users: %d" % added_users_count)
