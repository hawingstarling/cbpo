from django.apps import AppConfig

import sys

TESTING = sys.argv[1]


class FinancialConfig(AppConfig):
    name = 'app.financial'

    def ready(self):
        pass
