from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    default_app_config = 'user.MetaConfig'
    name = 'user'

    def ready(self):
        import user.signals
