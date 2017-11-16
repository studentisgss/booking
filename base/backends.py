from django.contrib.auth.backends import RemoteUserBackend


class BookingRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False
