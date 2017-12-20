from django.apps import AppConfig


class BrochureConfig(AppConfig):
    name = 'brochure'

    def ready(self):
        import brochure.signals
