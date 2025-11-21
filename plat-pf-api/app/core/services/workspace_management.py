import json, hashlib
import logging
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, transaction
from app.core.services.authentication_service import AuthenticationService
from app.core.services.portal_service import PortalService
from app.core.utils import get_name_from_email
from app.database.helper import get_connection_workspace
from app.financial.models import ClientPortal, Organization, User, UserPermission, ClientSettings
from app.selling_partner.models import SPOauthClientRegister
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister

logger = logging.getLogger(__name__)


class WorkspaceManagement:
    def __init__(self, client_id: str, is_supervisor: bool = False, *args, **kwargs):
        self.client_id = client_id
        self.client_db = get_connection_workspace(client_id)
        self.is_supervisor = is_supervisor
        self.args = args
        self.kwargs = kwargs
        self.portal_service = PortalService(client_id=client_id, **self.kwargs)

    def __call__(self, *args, **kwargs):
        logger.info(f"[{self.__class__.__name__}][__call__] {args} {kwargs}")

    def normalize_org_client_info(self, model_input: any, info: dict):
        assert len(info) > 0, f"Information normalize is not empty"
        fields_accept = [i.name for i in model_input._meta.fields]
        fields_request = list(info.keys())
        for field in fields_request:
            try:
                assert field not in fields_accept, f"[{self.__class__.__name__}][{self.client_id}] " \
                                                   f"field {field} match with model {model_input.__name__}"
                del info[field]
            except Exception as ex:
                continue
        return info

    def save_as_organization(self, org_id: str, data: dict):
        created = True
        try:
            org = Organization.all_objects.tenant_db_for(self.client_id).get(pk=org_id)
            Organization.all_objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=org_id).update(**data)
            # add client to datable config
            if self.client_db != DEFAULT_DB_ALIAS:
                Organization.all_objects.tenant_db_for(self.client_id).filter(pk=org_id).update(**data)
            org.refresh_from_db()
            created = False
        except Organization.DoesNotExist:
            org = Organization(**data)
            org.id = org_id
            Organization.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create([org], ignore_conflicts=True)
            if data != DEFAULT_DB_ALIAS:
                Organization.objects.tenant_db_for(self.client_id).bulk_create([org], ignore_conflicts=True)
        return org, created

    def save_as_workspace(self, client_id: str, user_id: str, data: dict):
        created = True
        try:
            obj = ClientPortal.all_objects.tenant_db_for(self.client_id).get(pk=client_id)
            ClientPortal.all_objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(pk=client_id).update(**data)
            # add client to datable config
            if self.client_db != DEFAULT_DB_ALIAS:
                ClientPortal.all_objects.tenant_db_for(self.client_id).filter(pk=client_id).update(**data)
            obj.refresh_from_db()
            created = False
        except ClientPortal.DoesNotExist:
            obj = ClientPortal(**data)
            obj.id = client_id
            ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create([obj], ignore_conflicts=True)
            if self.client_db != DEFAULT_DB_ALIAS:
                ClientPortal.objects.tenant_db_for(self.client_id).bulk_create([obj], ignore_conflicts=True)
            # setup service available for workspace
            from app.financial.jobs.imports import create_activity_sync_client_ps
            from app.database.jobs.db_table_template import sync_db_table_template_workspace
            from app.financial.jobs.schema_datasource import handler_generate_client_source
            from app.financial.jobs.register import register_ac_clients
            from app.financial.jobs.settings import handler_init_client_dashboard_widget, init_client_setting_default
            transaction.on_commit(
                lambda: {
                    init_client_setting_default(client_id=self.client_id),
                    sync_db_table_template_workspace(client_id=self.client_id),
                    register_ac_clients.delay(client_id=self.client_id),
                    create_activity_sync_client_ps.delay(client_id=self.client_id, user_id=user_id),
                    handler_generate_client_source.delay(client_id=self.client_id, access_token=settings.DS_TOKEN,
                                                         token_type='DS_TOKEN'),
                    handler_init_client_dashboard_widget.delay(client_ids=[self.client_id])
                },
                using=self.client_db
            )
        return obj, created

    def prefetch_user_sync_info(self, data: dict, owner: dict = {}):
        try:
            assert self.portal_service.jwt_token is not None, "JWT token is not None"
            user_auth = self.portal_service.get_user_info_auth()
            data.update(dict(user_sync_info=user_auth))
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.client_id}][prefetch_user_sync_info] {ex}")
            data.update(dict(user_sync_info=owner))

    def sync_status_of_client(self):
        self.sync_client_ps_to_pf()
        workspace: ClientPortal = ClientPortal.all_objects.tenant_db_for(self.client_id).get(pk=self.client_id)
        try:
            assert workspace.active is False or workspace.is_removed is True, "The workspace is activates in portal"
            # Disabled service that client is using
            # 1. MWS, SPAPI, Cart Rover
            SPOauthClientRegister.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id) \
                .update(latest=False)
            setting: ClientSettings = ClientSettings.objects.tenant_db_for(self.client_id).get(client_id=self.client_id)
            setting.ac_mws_enabled = False
            setting.ac_spapi_enabled = False
            setting.ac_cart_rover_enabled = False
            setting.save()
            # 2. Shopify register
            ShopifyPartnerOauthClientRegister.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id) \
                .update(enabled=False)
            #
            self.deactivates_register_ac_services()
        except Exception as ex:
            logger.info(f"[{self.__class__.__name__}][{self.client_id}][sync_status_of_client] {ex}")

    def deactivates_register_ac_services(self):
        from app.financial.jobs.register import register_mws_keys_setting, register_ac_clients_settings, \
            register_cart_rover_keys_setting
        from app.selling_partner.jobs.register import register_spapi_keys_setting
        # register deactivate to AC service
        transaction.on_commit(
            lambda: {
                register_ac_clients_settings([self.client_id]),
                register_mws_keys_setting([self.client_id]),
                register_spapi_keys_setting([self.client_id]),
                register_cart_rover_keys_setting([self.client_id]),
            }
        )

    def sync_client_ps_to_pf(self, user_id: str = None):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}]"
                    f"[sync_client_ps_to_pf] Begin ...")
        # generate audience token internally
        jwt_token = AuthenticationService.generate_jwt_token_internal_signature()
        headers = {
            f"Authorization": f"Bearer {jwt_token}"
        }
        rs = self.portal_service.get_client_information_internally(client_id=self.client_id, headers=headers)
        hash_data = hashlib.md5(json.dumps(rs).encode('utf-8')).hexdigest()
        #
        owner = rs.pop("owner", {})
        organization_data = rs.pop('organization', {})
        client_data = rs
        # find client portal exist ?
        client_id = client_data.pop("id")
        org_id = organization_data.pop("id")
        #
        obj = ClientPortal.objects.tenant_db_for(self.client_id).filter(pk=client_id, hash_data=hash_data).first()
        if obj:
            return obj
        #
        self.normalize_org_client_info(Organization, organization_data)
        # save info organization & client
        org, _ = self.save_as_organization(org_id, organization_data)
        client_data.update(dict(
            hash_data=hash_data,
            organization=org
        ))
        self.prefetch_user_sync_info(client_data, owner)
        self.normalize_org_client_info(ClientPortal, client_data)
        obj, _ = self.save_as_workspace(client_id, user_id, client_data)
        return obj

    def __auto_sync_info_user(self, user_info: dict):
        if not user_info:
            return
        try:
            user_id = user_info['user_id']
            data = {
                'username': user_info['username'],
                'email': user_info['email'],
                'first_name': user_info.get('first_name') or get_name_from_email(user_info['email']),
                'last_name': user_info['last_name'],
                'avatar': user_info['avatar']
            }
            hash_data = hashlib.md5(json.dumps(data).encode('utf-8')).hexdigest()
            queryset = User.objects.tenant_db_for(self.client_id).filter(user_id=user_id, hash=hash_data)
            if queryset.exists():
                return
            data.update({'hash': hash_data})
            User.objects.tenant_db_for(self.client_id).update_or_create(user_id=user_id, defaults=data)
        except Exception as ex:
            logger.error(f"[__auto_sync_info_user]: {ex}")

    def sync_client_setting_user_ps(self, user_id: str):
        assert user_id is not None, f"[{self.__class__.__name__}][sync_client_setting_user_ps] UserId is not empty"
        client_setting = self.portal_service.get_client_setting_user_ps(user_id)
        role = client_setting.get('role')
        module_info = {module.get('module'): module for module in client_setting.get('client_modules')}
        permissions_info = client_setting.get('permissions')
        self.__auto_sync_info_user(client_setting.get('user'))
        permissions = {}
        for permission in permissions_info:
            items = permissions.get(permission.get('module'), {})
            items[permission.get('permission')] = permission.get('enabled')
            permissions[permission.get('module')] = items
        #
        client = self.sync_client_ps_to_pf(user_id=user_id)
        query_set = UserPermission.objects.tenant_db_for(self.client_id).filter(user_id=user_id, client=client)
        for module in module_info:
            try:
                hash_data = {
                    'module': module,
                    'module_enabled': module_info[module].get('enabled'),
                    'role': role.get('key'),
                    'permissions': permissions[module]
                }
                #
                hash_data = hashlib.md5(json.dumps(hash_data).encode('utf-8')).hexdigest()
                if query_set.filter(hash_data=hash_data).exists():
                    continue
                UserPermission.objects.tenant_db_for(self.client_id) \
                    .update_or_create(user_id=user_id,
                                      client_id=self.client_id,
                                      module=module,
                                      defaults=dict(role=role.get('key'),
                                                    role_name=role.get('name'),
                                                    module_enabled=module_info[module].get('enabled'),
                                                    permissions=permissions[module],
                                                    hash_data=hash_data)
                                      )
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][sync_client_setting_user_ps] {ex}")
