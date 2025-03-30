from django.apps import AppConfig


class MetaConfig(AppConfig):
    default_app_config = 'meta.MetaConfig'
    name = 'meta'

    def ready(self):
        import meta.signals
