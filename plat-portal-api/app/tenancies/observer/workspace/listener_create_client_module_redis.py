from django.core.cache import cache

from app.core.logger import logger
from app.tenancies.models import ClientModule
from app.tenancies.observer.interface_listener import IListener


class CreateClientModuleRedisListener(IListener):
    def run(self, **kwargs):
        client_id = kwargs.get("client_id")
        client_modules = ClientModule.objects.filter(client_id=client_id)

        key = {"client_id": str(client_id)}
        values = [{"module": ele.module, "enabled": ele.enabled} for ele in client_modules]
        try:
            cache.set(key, values)
        except Exception as error:
            logger.error(f"[{self.__class__.__name__}] {error}")
            raise error
