from django.apps import AppConfig


class OemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.oem'

    def ready(self):
        import apps.oem.signals