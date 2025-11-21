from typing import Dict, List

from app.financial.observer.interface_listener import IListener
from app.financial.observer.item_aspect.listener_sale_item_mapping_cog import SaleItemMappingCogListener

ITEM_ASPECT_EVENT = "ITEM_ASPECT"


class __Publisher:
    """
    Observer Pattern
    Manage typical actions on module
    """

    event: Dict[str, List[IListener]] = {
        ITEM_ASPECT_EVENT: [
            SaleItemMappingCogListener()
        ],
        "SALE_ITEM_ASPECT": [],
        "CREATE_ORG_MEMBER": [],
        "CREATE_WORKSPACE_MEMBER": [],
        "UPDATE_WORKSPACE_MODULE": [],
        "DELETE_MEMBER": []
    }

    event_countdown: Dict[str, int] = {
        "UPDATE_WORKSPACE_MODULE": 5
    }

    def subscribe(self, event_type: str, listener):
        # TODO: dynamically subscribe
        pass

    def unsubscribe(self, even_type: str):
        # TODO: dynamically unsubscribe
        pass

    def notify(self, event_type: str, **kwargs):
        if event_type not in self.event:
            raise Exception("key event error.")

        for listener in self.event[event_type]:
            listener.run(**kwargs)


publisher = __Publisher()
