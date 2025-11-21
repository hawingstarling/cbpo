from app.financial.models import Activity, ClientPortal, Brand
from app.database.helper import get_connection_workspace
from app.financial.variable.activity_variable import (
    SYNC_CLIENT_PORTAL_KEY, IMPORT_ITEM_DATA_KEY, SALE_ITEM_DATA_ACTION_KEYS,
    IMPORT_SALE_ITEM_DATA_KEY, ITEM_DATA_ACTION_KEYS, IMPORT_FEDEX_SHIPMENT_DATA_KEY,
    IMPORT_APP_EAGLE_PROFILE_DATA_KEY, REVOKED_ACTION_KEY, DELETE_BRAND_DATA_KEY)


class ActivityService:

    def __init__(self, client_id, user_id, **kwargs):
        self.client_id = client_id
        self.client_db = get_connection_workspace(client_id)
        self.user_id = user_id
        self.client = ClientPortal.objects.tenant_db_for(self.client_id).get(pk=self.client_id)
        self.kwargs = kwargs

    def create_activity_import_sale_data(self):
        data = {
            'action': IMPORT_SALE_ITEM_DATA_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'SaleItem'
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_action_sale_data(self, action_key: str, import_id: str = None, sale_item_ids=[]):
        assert action_key in SALE_ITEM_DATA_ACTION_KEYS, "action key is invalid"
        data = {
            'action': action_key,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'SaleItem',
                'bulk_import_id': import_id
            }
        }
        if sale_item_ids:
            data['data'].update({'sale_item_ids': sale_item_ids})
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_revoke_action(self, module: str, import_id: str = None, **kwargs):
        data = {
            'action': REVOKED_ACTION_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': module,
                'bulk_import_id': import_id
            }
        }
        try:
            command = kwargs.get('command')
            if command:
                data['data'].update(dict(command=command))
            sources = kwargs.get('sources')
            if sources:
                data['data'].update(dict(sources=sources))
            custom_report_type = kwargs.get('custom_report_type')
            if custom_report_type:
                data['data'].update(dict(custom_report_type=custom_report_type))
        except Exception as ex:
            pass
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_sync_client_ps(self):
        data = {
            'action': SYNC_CLIENT_PORTAL_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_import_item_data(self):
        data = {
            'action': IMPORT_ITEM_DATA_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'ItemModule'
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_action_item_data(self, action_key: str, item_ids: [str]):
        assert action_key in ITEM_DATA_ACTION_KEYS, "action key is invalid"
        data = {
            'action': action_key,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'ItemModule',
                'item_ids': item_ids
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_import_fedex_shipment(self):
        data = {
            'action': IMPORT_FEDEX_SHIPMENT_DATA_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'FedExShipmentModule'
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_import_app_eagle_profile(self):
        data = {
            'action': IMPORT_APP_EAGLE_PROFILE_DATA_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'module': 'AppEagleProfile'
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_delete_brand_data(self, brand_id: str):
        brand = Brand.all_objects.tenant_db_for(self.client_id).get(id=brand_id)
        data = {
            'action': DELETE_BRAND_DATA_KEY,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': {
                'client_id': self.client_id,
                'client_name': self.client.name,
                'brand_name': brand.name
            }
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)

    def create_activity_by_action(self, action: str, **kwargs):
        data = {
            'action': action,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'data': kwargs
        }
        Activity.objects.tenant_db_for(self.client_id).create(**data)
