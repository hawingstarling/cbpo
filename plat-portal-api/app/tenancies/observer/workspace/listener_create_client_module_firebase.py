from app.core.firebase import ref as ref_firebase
from app.core.logger import logger
from app.tenancies.models import ClientModule
from app.tenancies.observer.interface_listener import IListener

client_module_ref = ref_firebase.child("client_module")


class CreateClientModuleFirebaseListener(IListener):
    def run(self, **kwargs):
        client_id = kwargs.get("client_id")
        client_modules = ClientModule.objects.filter(client_id=client_id)

        values = [{"module": ele.module, "enabled": ele.enabled} for ele in client_modules]

        try:
            client_module_ref.update({
                f"{client_id}": values
            })
        except Exception as error:
            logger.error(f"[{self.__class__.__name__}] {error}")
            raise error
