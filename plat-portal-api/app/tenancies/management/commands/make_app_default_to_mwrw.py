from django.core.management.base import BaseCommand
import logging
from django.db import transaction
from app.tenancies.models import Client, AppClientConfig
from django.db.models import Q

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = "This is command migrate all client to app client config table and set app default MW/RW"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Step by step:
            1. get all record app client config (app=mwrw)
            2. get all client not found in 1
            3. make app MW/RW to default for 2
        :param args:
        :param options:
        :return:
        """
        print("Begin migrate all client to app MW/RW client config")
        try:
            # 1.
            app_client_configs = AppClientConfig.objects.filter(app="mwrw").values_list("client_id", flat=True)
            # 2.
            client_ids_migrate = Client.objects.filter(~Q(pk__in=app_client_configs))
            # 3.
            data_insert = []
            with transaction.atomic():
                for client in client_ids_migrate:
                    print("Migrate client : {}".format(client.name))
                    obj = AppClientConfig(client=client, app="mwrw", enabled=True)
                    data_insert.append(obj)
            AppClientConfig.objects.bulk_create(data_insert)
        except Exception as ex:
            logger.error("Migrate app client config: {}".format(ex))
        print("End migrate all client to app MW/RW client config")
