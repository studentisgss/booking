from django.contrib.auth.middleware import PersistentRemoteUserMiddleware


class BookingRemoteUserMiddleware(PersistentRemoteUserMiddleware):
    header = 'shib_id'
