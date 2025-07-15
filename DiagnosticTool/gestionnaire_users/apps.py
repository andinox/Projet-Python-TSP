from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gestionnaire_users"


def ready(self):
    import gestionnaire_users.signals
