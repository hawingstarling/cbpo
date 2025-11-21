from app.tenancies.models import Client
from app.tenancies.observer.interface_listener import IListener
from app.tenancies.services import AppClientConfigService


class CreateAppProfileListener(IListener):
    def run(self, **kwargs):
        client_id, app = kwargs.get("client_id"), kwargs.get("app")
        client = Client.objects.get(id=client_id)
        AppClientConfigService.create_client_app_profile(
            client=client, app=app, enabled=True
        )
