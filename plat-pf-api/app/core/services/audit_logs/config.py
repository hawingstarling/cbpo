from app.financial.variable.job_status import SKU_VAULT_JOB, CART_ROVER_JOB, CONNECT_3Pl_CENTRAL_JOB, \
    EXTENSIV_COG_CALCULATION_JOB

SYSTEM_DC = 'System DC Auto Update'
SYSTEM_AC = 'System AC Auto Update'
SYSTEM_COG = 'System COG Auto Update'
SYSTEM_COMMON = 'System Common Auto Update'
SYSTEM_FEDEX = 'System FedEx Shipment Auto Update'
SYSTEM_BRAND_SETTINGS = 'System Brand Settings Auto Update'
SYSTEM_FULFILLMENT_MFN_CLASSIFICATION = 'System Fulfillment MFN Classification Auto Update'


class AdditionalDataCallable:
    def __init__(self, obj, label_actor=None):
        self.val = obj
        self.label = label_actor

    def __call__(self, *args, **kwargs):
        if not self.val:
            actor_info = {
                "last_name": "Live Feed",
                "first_name": "System"
            }
            label = self.label if self.label else "system"
            if label == SYSTEM_DC:
                actor_info = {
                    "last_name": "DC Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_AC:
                actor_info = {
                    "last_name": "AC Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_BRAND_SETTINGS:
                actor_info = {
                    "last_name": "Brand Settings Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_FEDEX:
                actor_info = {
                    "last_name": "FedEx Shipment Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_COG:
                actor_info = {
                    "last_name": "COG Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_COMMON:
                actor_info = {
                    "last_name": "Common Auto Update",
                    "first_name": "System"
                }
            if label == SYSTEM_FULFILLMENT_MFN_CLASSIFICATION:
                actor_info = {
                    "last_name": "Fulfillment MFN Classification Auto Update",
                    "first_name": "System"
                }
            if label == SKU_VAULT_JOB:
                actor_info = {
                    "last_name": "MFN-Prime by SKUVault",
                    "first_name": ""
                }
            if label == CART_ROVER_JOB:
                actor_info = {
                    "last_name": "MFN-Prime by CartRover",
                    "first_name": ""
                }
            if label == CONNECT_3Pl_CENTRAL_JOB:
                actor_info = {
                    "last_name": "MFN-Prime by 3PL Central",
                    "first_name": ""
                }
            if label == EXTENSIV_COG_CALCULATION_JOB:
                actor_info = {
                    "last_name": "Extensiv Auto Update",
                    "first_name": ""
                }
            return {
                "actor": label,
                "actor_info": actor_info
            }
        return {
            "actor": "user",
            "actor_info": self.val
        }
