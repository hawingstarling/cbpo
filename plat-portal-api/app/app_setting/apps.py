from django.apps import AppConfig


class AppSettingConfig(AppConfig):
    name = "app.app_setting"

    def ready(self):
        from . import receivers  # noqa
