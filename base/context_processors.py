from django.conf import settings


def demo(request):
    return {'DEMO': settings.DEMO}


def authenticated(request):
    return {'AU': request.user.is_authenticated()}
