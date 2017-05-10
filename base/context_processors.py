from django.conf import settings


def demo(request):
    return {'DEMO': settings.DEMO}
