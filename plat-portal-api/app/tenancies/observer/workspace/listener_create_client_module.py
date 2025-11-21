from typing import List

from app.core.services.app_confg import AppService
from app.tenancies.models import ClientModule, Client
from app.tenancies.observer.interface_listener import IListener


class CreateClientModuleListener(IListener):
    def run(self, **kwargs):
        client_id, app = kwargs.get("client_id"), kwargs.get("app")
        client = Client.objects.get(id=client_id)

        all_modules: List[str] = AppService().get_all_modules_app()
        enabled_modules: List[str] = AppService().get_modules_app(app_name=app)

        bulk_obj = []

        for module in all_modules:
            enabled = True if module in enabled_modules else False
            bulk_obj.append(ClientModule(client=client, module=module, enabled=enabled))

        ClientModule.objects.bulk_create(bulk_obj)
