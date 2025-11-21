import uuid
from django.db import DatabaseError
from plat_import_lib_api.static_variable.raw_data_import import RAW_IGNORED_TYPE
from psycopg2 import OperationalError
import copy
import logging
import time
from plat_import_lib_api.models import PROCESSED, REVERTING, REVERTED
from app.financial.import_template.sale_item_bulk_edit import SaleItemBulkEdit
from app.financial.models import FulfillmentChannel, SaleItem
from app.financial.services.sale_item_bulk.sale_item_bulk_base import SaleItemBulkBaseModuleService
from app.financial.sub_serializers.client_sale_item_log import SaleItemLogSerializer, ClientSaleLogSerializer
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import ClientSaleItemBulkEditSerializer
from app.financial.variable.bulk_command_variable import BULK_COMMAND_CHOICE
from app.financial.variable.sale_item import JOB_ACTION, BULK_EDIT_JOB

logger = logging.getLogger(__name__)


class SaleItemBulkEditModuleService(SaleItemBulkBaseModuleService):
    module = SaleItemBulkEdit
    serializer_class = ClientSaleItemBulkEditSerializer

    def __init__(self, bulk_id: str = None, jwt_token: str = None, user_id: str = None, client_id: str = None):
        super().__init__(bulk_id=bulk_id, jwt_token=jwt_token, user_id=user_id, client_id=client_id)
        self.updates = self.bulk.meta.get('updates', [])
        self.update_operations = {update['column']: update for update in self.updates}
        self.fulfillment_mfn_prime = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='MFN-Prime')
        self.fields_sale_item_accept_validate = self.fields_sale_item_accept + ['style_variant', 'size_variant']

    def _process(self):
        try:
            while True:
                start_chunk = time.time()
                if not self.query_set_processing.exists():
                    break

                bulk_data = self.query_set_processing.order_by('index')[:self.bulk_data_chunk_size]
                self.items_chunk_map = {uuid.UUID(item.key_map): item for item in bulk_data}
                ids = list(self.items_chunk_map.keys())
                logger.info(f'[{self.__class__.__name__}][process] {self.bulk.pk} - Items to processed: {len(ids)}')
                try:
                    ids = self._process_allow_sale_data_update_from(ids)
                    if len(ids) > 0:
                        sale_items = SaleItem.objects.tenant_db_for(self.client_id) \
                            .filter(id__in=ids).order_by('created')
                        # Start bulk_edit process for items in each chunk
                        if self.command == BULK_COMMAND_CHOICE[0][0]:
                            self.__process_edit(sale_items=sale_items)
                        # Start bulk_delete process
                        elif self.command == BULK_COMMAND_CHOICE[1][0]:
                            self.__process_delete(sale_items=sale_items)
                        else:
                            pass
                except OperationalError or DatabaseError:
                    continue
                except Exception as ex:
                    self._update_error_summary(self.command, message=str(ex))
                    logger.error(f'[{self.__class__.__name__}][process]{self.command} {self.bulk.pk} {ex}')

                # Update bulk_info
                self._update_bulk_info()

                # Sync edited sale_items to datasource
                self._sync_datasource(ids)

                end_chunk = time.time()
                logger.info(f'[{self.__class__.__name__}][process]{self.bulk.pk} '
                            f'Time executed bulk-edit/delete sale item chunk: {end_chunk - start_chunk}')

                # Stop process if job is `cancelled`
                if self.bulk.status in [PROCESSED, REVERTED]:
                    break
        except Exception as ex:
            logger.error(f'[{self.__class__.__name__}][_process] {self.command} - {self.bulk.pk} {ex}')

    def __process_edit(self, sale_items):
        """
        Process bulk-edit on multiple sale-items
        @param sale_items: list of items to be updated
        @return:
        """
        for index, sale_item in enumerate(sale_items):
            sale_item_id = sale_item.pk
            raw_ins = self.items_chunk_map[sale_item_id]
            # Item to be cached
            try:
                #
                raw_ins.meta_addition = {'command': self.command, 'processing_errors': []}
                raw_ins.modified = self.time_now
                #
                context_data = dict(instance=sale_item, bulk_edit=True)
                if self.bulk.status == REVERTING:
                    try:
                        original_values = copy.deepcopy(raw_ins.data_map_config['last_values'])
                        assert len(original_values) > 0, "Not found data origin values"
                        context_data.update(data=original_values, bulk_edit=False)
                    except Exception as ex:
                        # logger.error(f"[{self.__class__.__name__}] {ex}")
                        raw_ins.status = self._status_complete
                        raw_ins.is_valid = False
                        raw_ins.is_complete = False
                        raw_ins.type = RAW_IGNORED_TYPE
                        raw_ins.processing_errors = {'code': f'{sale_item_id}', 'message': f"{ex}"}
                        self.items_chunk_map[sale_item_id] = raw_ins
                        continue
                #
                # Calculate data from origin-value and operations and validate new value
                serializer, list_error, dict_error = self._validate_update_data(**context_data)
                # Validate updated data
                if not serializer.is_valid():
                    raw_ins.status = self._status_complete
                    raw_ins.is_valid = False
                    raw_ins.is_complete = False
                    raw_ins.type = RAW_IGNORED_TYPE
                    raw_ins.processing_errors += list_error
                    # Update items for json_last_cache
                    self.items_chunk_map[sale_item_id] = raw_ins
                    continue

                # Parse value to string for caching
                initial_data = {key: str(value) for (key, value) in serializer.initial_data.items()}
                # last value
                log_sale_data = ClientSaleLogSerializer(sale_item.sale).log_data
                log_item_data = SaleItemLogSerializer(sale_item).log_data
                log_data = {**log_sale_data, **log_item_data}
                last_values = {}
                for key in initial_data.keys():
                    if key == 'style_variant':
                        val = log_data.get('style')
                    elif key == 'size_variant':
                        val = log_data.get('size')
                    else:
                        val = log_data.get(key)
                    last_values.update({key: val})
                raw_data = {'initial_data': initial_data, 'last_values': last_values}
                raw_ins.data_map_config = raw_data

                # Create updated sale_item instance and log_entry
                validated_item_data = copy.deepcopy(serializer.validated_data)
                __has_sale_item_updated = any(
                    key in self.fields_sale_item_accept_validate for key in validated_item_data.keys())
                __has_sale_updated_is_prime = any(
                    key == 'is_prime' and validated_item_data.get('is_prime', False) is True for key in
                    validated_item_data.keys())
                if __has_sale_item_updated or __has_sale_updated_is_prime:
                    serializer.context.update({'changed_is_prime': __has_sale_updated_is_prime,
                                               'fulfillment_mfn_prime': self.fulfillment_mfn_prime})
                    sale_item, log_entry = serializer.update(instance=sale_item, validated_data=validated_item_data)

                    # Ignore items that have no changes
                    if log_entry:
                        self.sale_item_bulk.append(sale_item)
                        self.log_entry_bulk.append(log_entry)

                # Create updated sale instance and log_entry if state is updated
                validated_sale_data = copy.deepcopy(serializer.validated_data)
                __has_sale_updated = any(key in self.fields_sale_accept for key in validated_sale_data.keys())
                __has_sale_affected_by_item = any(
                    key in ['sale_date', 'sale_status', 'profit_status'] for key in validated_sale_data.keys())
                if __has_sale_updated:
                    sale, sale_log_entry = serializer.update_single_data_sale(sale=sale_item.sale,
                                                                              validated_data=validated_sale_data)
                    if sale_log_entry:
                        # set dirty all item of sale for generate DS
                        self._sale_ids_affected.add(sale_item.sale.id)
                        self.sale_bulk.append(sale)
                        self.log_entry_bulk.append(sale_log_entry)
                if __has_sale_affected_by_item:
                    self._sale_ids_affected.add(sale_item.sale.id)

                # Update items for json_last_cache
                raw_ins.is_valid = True
                raw_ins.status = self._status_complete
                raw_ins.is_complete = True
                raw_ins.processing_errors = []
                self.items_chunk_map[sale_item_id] = raw_ins
            except OperationalError or DatabaseError as ex:
                raise ex
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}] {ex}")
                raw_ins.is_valid = False
                raw_ins.status = self._status_complete
                raw_ins.is_complete = False
                raw_ins.type = RAW_IGNORED_TYPE
                raw_ins.processing_errors += [{'code': 'system', 'message': str(ex)}]
                # Update items for json_last_cache
                self.items_chunk_map[sale_item_id] = raw_ins

        #
        self._bulk_update()

    def __process_delete(self, sale_items):
        """
        Process bulk-delete on multiple sale-items
        @param sale_items: list of items to be deleted
        @return:
        """
        self.sale_item_bulk = []
        for sale_item in sale_items:
            # Soft-delete sale-item
            obj = copy.deepcopy(sale_item)
            obj.dirty = True
            obj.financial_dirty = True
            obj.is_removed = True

            self.sale_item_bulk.append(obj)
            self._sale_ids_affected.add(sale_item.sale.id)
        # update status success
        self._update_success_summary()
        #
        self._bulk_update()

    def _validate_update_data(self, instance, **kwargs):
        """
        @param instance: original sale-item
        @param kwargs:
        @return:
        """
        bulk_edit = kwargs.get('bulk_edit', False)

        # ClientSaleItemBulkEditSerializer calculate `updated_data` from `update_operations`
        operations = getattr(self, 'update_operations', {})
        data = kwargs.get('data', operations)
        context = {
            'kwargs': {JOB_ACTION: BULK_EDIT_JOB, "client_id": self.client_id},
            'is_remove_cogs_refunded': getattr(self.client_setting, "is_remove_cogs_refunded", False)
        }
        serializer = self.serializer_class(instance=instance, data=data, bulk_edit=bulk_edit, partial=True,
                                           context=context)
        list_error = []
        dict_error = {'id': instance.pk}
        if not serializer.is_valid():
            for (key, error) in serializer.errors.items():
                message = ' '.join(error)
                list_error.append({'code': key, 'message': message})
                dict_error[key] = message
        return serializer, list_error, dict_error
