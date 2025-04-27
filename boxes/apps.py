from django.apps import AppConfig


class BoxesConfig(AppConfig):
    """App configuration for the boxes app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boxes'

    def ready(self):
        import boxes.signals
