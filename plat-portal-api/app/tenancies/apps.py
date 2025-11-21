from django.apps import AppConfig
from django.conf import settings

import sys

TESTING = sys.argv[1]


class TenanciesConfig(AppConfig):
    name = 'app.tenancies'

    def ready(self):
        if TESTING == 'test':
            return
        else:
            from .signals import (automatic_permissions, change_notification_client_status,
                                  change_notification_organization_status, signal_user)
