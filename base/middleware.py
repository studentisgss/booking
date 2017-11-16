from django.contrib.auth.middleware import PersistentRemoteUserMiddleware


class BookingRemoteUserMiddleware(PersistentRemoteUserMiddleware):
    header = 'SHIB_ID'
