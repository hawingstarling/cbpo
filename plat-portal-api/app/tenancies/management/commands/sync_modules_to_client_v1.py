import logging
from django.core.management.base import BaseCommand
from app.core.services.app_confg import AppService
from app.tenancies.config_static_variable import APP_MODULE_BUILD_PROFILE
from app.tenancies.models import Client, ClientModule, AppClientConfig
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This is command migrate all module missing to all client."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Update all module missing to client and check app status enable module
        :param args:
        :param options:
        :return:
        """
        print("Start sync modules to client")
        try:
            all_modules = AppService.get_all_modules_app()
            # get all client with status active
            clients = Client.objects.filter(active=True)
            if not clients:
                print("Not found client to update")
                return
            with transaction.atomic():
                for client in clients.iterator():
                    print("update modules to client {}".format(client.pk))
                    # get module enable
                    app_client = AppClientConfig.objects.filter(client=client)
                    modules_enable = []
                    for item in app_client:
                        if item.enabled:
                            modules_enable += APP_MODULE_BUILD_PROFILE[item.app]
                    # remove module duplicates
                    modules_enable = set(modules_enable)
                    # Update module
                    self.update_module_to_client(client, modules_enable, all_modules)
        except Exception as ex:
            print("Error in timer: %r" % ex)
        print("End sync modules to client")

    def update_module_to_client(self, client: Client, modules_app_enable: set, all_modules: list = []):
        for module in all_modules:
            ClientModule.objects.get_or_create(client=client, module=module,
                                               defaults={'enabled': module in modules_app_enable})
