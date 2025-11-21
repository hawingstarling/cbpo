import logging
from auditlog.receivers import *
from dictdiffer import diff
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.encoding import smart_str
from app.core.context import AppContext
from app.core.services.audit_logs.config import AdditionalDataCallable
from app.core.services.user_permission import get_user_permission
from app.financial.models import LogClientEntry
from app.database.helper import get_connection_workspace
from app.financial.services.postgres_fulltext_search import PostgresFulltextSearch
from app.financial.sub_serializers.user_serializer import UserSerializer

logger = logging.getLogger(__name__)

SALE_LEVEL = 0
SALE_ITEM_LEVEL = 1
SALE_ITEM_FINANCIAL_LEVEL = 2
SALE_ITEM_TRANS_LEVEL = 3
SALE_SHIPPING_INVOICE_LEVEL = 4


class AuditLogCoreManager(object):
    __actor_name = 'admin'

    def __init__(self, client_id, **kwargs):
        self.client_id = str(client_id)
        self.client_db = get_connection_workspace(self.client_id)
        self.kwargs = kwargs

    def _get_pk_value(self, instance):
        """
        Get the primary key field value for a model instance.

        :param instance: The model instance to get the primary key for.
        :type instance: Model
        :return: The primary key value of the given model instance.
        """
        pk_field = instance._meta.pk.name
        pk = getattr(instance, pk_field, None)

        # Check to make sure that we got an pk not a model object.
        if isinstance(pk, models.Model):
            pk = self._get_pk_value(pk)
        return pk

    def set_actor_name(self, name: str):
        self.__actor_name = name
        return self

    @property
    def user_id(self):
        try:
            user_id = self.kwargs['user_id']
        except Exception as ex:
            user_id = AppContext.instance().user_id
        return user_id

    @property
    def jwt_token(self):
        try:
            jwt_token = self.kwargs['jwt_token']
        except Exception as ex:
            jwt_token = AppContext.instance().jwt_token
        return jwt_token

    @property
    def get_additional_data_log(self):
        try:
            user_permission = get_user_permission(self.jwt_token, self.client_id, self.user_id)
            user_info = UserSerializer(user_permission.user).data
            additional_data = AdditionalDataCallable(user_info, 'user')
        except Exception as ex:
            additional_data = AdditionalDataCallable(None, self.__actor_name)
        return additional_data

    @property
    def get_additional_system_data_log(self):
        return AdditionalDataCallable(None, self.__actor_name)

    def create_log_entry_instance(self, level: int = 1, origin=None, target=None, action=LogClientEntry.Action.CREATE):
        pk = self._get_pk_value(target)
        changes = self.get_diff(origin, target, level)
        if changes:
            data = {}
            data.setdefault('content_type', ContentType.objects.db_manager(
                using=self.client_db).get_for_model(target))
            data.setdefault('object_pk', pk)
            data.setdefault('object_repr', smart_str(target))
            data.setdefault('changes', json.dumps(changes))
            data.setdefault('action', action)

            if isinstance(pk, int):
                data.setdefault('object_id', pk)

            get_additional_data = self.get_additional_data_log
            if callable(get_additional_data):
                data.setdefault('additional_data', get_additional_data())
            return LogClientEntry(**data)
        return None

    def get_logs(self, instance, keyword: str = None):
        logs_by_pk = LogClientEntry.objects.tenant_db_for(
            self.client_id).filter(object_pk=instance.pk)
        if keyword is not None:
            search_handler = PostgresFulltextSearch(model_objects_manager=logs_by_pk, fields_config=None,
                                                    sort_config=None)
            return search_handler.search(keyword)
        return logs_by_pk

    def get_logs_from_ids(self, ids: [str], keyword: str = None):
        log_by_ids = LogClientEntry.objects.tenant_db_for(
            self.client_id).filter(object_pk__in=ids)
        if keyword is not None:
            search_handler = PostgresFulltextSearch(
                log_by_ids, fields_config=None, sort_config=None)
            return search_handler.search(keyword)
        return log_by_ids

    def get_diff(self, first_instance: any, second_instance: any, level: int = 1):
        from app.financial.sub_serializers.client_sale_item_log import SaleItemLogSerializer, ClientSaleLogSerializer, \
            SaleItemFinancialLogSerializer
        from app.financial.sub_serializers.sale_item_trans_event_serializer import SaleItemTransEventLogSerializer
        from app.financial.sub_serializers.shipping_invoice_serializer import ShippingInvoiceLogSerializer
        res_changes = {}
        try:
            args = {
                SALE_LEVEL: ClientSaleLogSerializer,
                SALE_ITEM_LEVEL: SaleItemLogSerializer,
                SALE_ITEM_FINANCIAL_LEVEL: SaleItemFinancialLogSerializer,
                SALE_ITEM_TRANS_LEVEL: SaleItemTransEventLogSerializer,
                SALE_SHIPPING_INVOICE_LEVEL: ShippingInvoiceLogSerializer
            }
            serializer_class = args.get(level, SaleItemLogSerializer)
            first_instance = serializer_class(first_instance).log_data
            second_instance = serializer_class(second_instance).log_data

            changes = diff(first_instance, second_instance)
            for change in changes:
                res_changes.update({
                    change[1]: [str(change[2][0]), str(change[2][1])]
                })
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
        return res_changes

    def create_log_entry_from_compared_changes(self, instance, changes: dict, action=LogClientEntry.Action.CREATE):
        pk = self._get_pk_value(instance)
        if changes:
            data = {}
            data.setdefault('content_type',
                            ContentType.objects.db_manager(using=self.client_db).get_for_model(instance))
            data.setdefault('object_pk', pk)
            data.setdefault('object_repr', smart_str(instance))
            data.setdefault('changes', json.dumps(
                changes, cls=DjangoJSONEncoder))
            data.setdefault('action', action)

            if isinstance(pk, int):
                data.setdefault('object_id', pk)

            get_additional_data = self.get_additional_data_log
            if callable(get_additional_data):
                data.setdefault('additional_data', get_additional_data())
            return LogClientEntry(**data)
        return None
