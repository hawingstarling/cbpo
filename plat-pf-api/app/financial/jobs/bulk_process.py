import json
import logging
from celery import current_app
from plat_import_lib_api.models import DataImportTemporary, FAILURE
from app.financial.jobs.brand_setting import BRAND_SETTING_MODULE_UPDATE_SALES
from app.financial.models import ClientSettings, BrandSetting
from app.financial.services.brand_settings.ship_cost_calculation_for_sale_item import BrandSettingUpdateSaleItem
from app.database.helper import get_connection_workspace
from app.financial.services.financial_notification import EmailServices
from app.financial.variable.bulk_module_service import bulk_module_config
from app.job.base.tasks import TaskBasement

logger = logging.getLogger(__name__)

TIME_LIMIT_BULK_PROCESS = (60 * 30)  # seconds


class BulkProcessBasement(TaskBasement):
    track_started = True
    expires = (60 * 30)

    soft_time_limit = TIME_LIMIT_BULK_PROCESS
    time_limit = TIME_LIMIT_BULK_PROCESS + 5

    def run(self, *args, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        # celery event
        client_id = kwargs.get('client_id')
        client_settings = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
        if self.__should_sent_notification(task_id, client_settings.time_bulk_processing_notification, kwargs) is True:
            self.__send_notification(client_id, retval, client_settings.time_bulk_processing_notification, kwargs)
        super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # celery event
        client_id = kwargs.get('client_id')
        client_settings = ClientSettings.objects.tenant_db_for(client_id).get(client_id=client_id)
        import_temp_id = kwargs.get('import_temp_id')
        client_db = get_connection_workspace(client_id)
        data_import_lib = DataImportTemporary.objects.db_manager(using=client_db).get(id=import_temp_id)
        data_import_lib.log = f'{einfo}'
        data_import_lib.progress = 100
        data_import_lib.status = FAILURE
        data_import_lib.save()
        if self.__should_sent_notification(task_id, client_settings.time_bulk_processing_notification, kwargs) is True:
            # TODO: send notification for exception failure
            pass
        super().on_failure(exc, task_id, args, kwargs, einfo)

    @classmethod
    def __should_sent_notification(cls, task_id, time_bulk_processing_notification, kwargs) -> bool:
        try:
            client_db = get_connection_workspace(kwargs.get('client_id'))
            data_import_lib = DataImportTemporary.objects.db_manager(using=client_db).get(
                id=kwargs.get('import_temp_id'))
            time_processed_delta = (data_import_lib.process_completed - data_import_lib.created).total_seconds()
            return time_processed_delta >= time_bulk_processing_notification
        except Exception as ex:
            logger.info(f"[__should_sent_notification][{task_id}][{kwargs}] {ex}")
        return False

    @classmethod
    def __send_notification(cls, client_id, retval, time_bulk_processing_notification, kwargs):
        try:
            client_db = get_connection_workspace(client_id)
            import_temp_id = kwargs.get('import_temp_id')
            data_import_lib = DataImportTemporary.objects.db_manager(using=client_db).get(id=import_temp_id)
            description = {"uuid": import_temp_id,
                           "action": str(retval),
                           "process_started": data_import_lib.process_started,
                           "process_completed": data_import_lib.process_completed,
                           "total_items": data_import_lib.info_import_file['summary']['total'],
                           "total_items_success": data_import_lib.info_import_file['summary']['success'],
                           "minutes": time_bulk_processing_notification}
            items = json.loads(data_import_lib.json_data_last_cache)
            items = [{'id': item['id'], **item.get("_meta")} for item in items]
            user_information = data_import_lib.meta.get('user_info')

            username = user_information.get('last_name', 'there')
            email = user_information.get('email')
            EmailServices().send_bulk_processing('PF Development', username, description, items, [email])
        except Exception as error:
            logger.error(f'[__send_notification][BulkProgress] {error}')


class BulkProcessChunkBasement(BulkProcessBasement):
    expires = (60 * 5)
    soft_time_limit = None


@current_app.task(bind=True, base=BulkProcessChunkBasement)
def processing_bulk_module_chunk(self, module, import_temp_id: str = None, jwt_token: str = None,
                                 client_id: str = None, user_id: str = None):
    assert module in list(bulk_module_config.keys()), "Module not in bulk_module_config"
    logger.info(f"[Tasks][{self.request.id}][{module}] Begin implement processing bulk-module...")
    module_service_class = bulk_module_config.get(module)
    module_service = module_service_class(bulk_id=import_temp_id, jwt_token=jwt_token, client_id=client_id,
                                          user_id=user_id)
    module_service.start_processing()
    return f'PF BUlK {module.upper()}'  # for message in notification


@current_app.task(bind=True, base=BulkProcessBasement)
def processing_bulk_brand_setting(self, import_temp_id: str = None, client_id: str = None, **kwargs):
    logger.info(f"[processing_bulk_brand_setting][{self.request.id}][{client_id}]"
                f"[{import_temp_id}] Begin implement processing bulk-module...")
    brand_setting_id = kwargs.get('brand_setting_id')
    brand_setting = BrandSetting.objects.tenant_db_for(client_id).get(id=brand_setting_id)
    is_recalculate = kwargs.get('is_recalculate')
    from_date = kwargs.get('from_date')
    to_date = kwargs.get('to_date')
    handler = BrandSettingUpdateSaleItem(client_id, brand_setting, is_recalculate, from_date, to_date,
                                         import_temp_id, 5000)
    handler.update()
    return 'PF BRAND SETTINGS UPDATE SALE ITEMS'  # for message in notification


@current_app.task(bind=True)
def bulk_handler(self, module: str, jwt_token: str = None, import_temp_id: str = None, client_id: str = None,
                 user_id: str = None, *args, **kwargs):
    assert module in list(bulk_module_config.keys()), "Module not in bulk_module_config"

    if module == BRAND_SETTING_MODULE_UPDATE_SALES:
        processing_bulk_brand_setting(import_temp_id=import_temp_id, client_id=client_id, **kwargs)
        return

    module_service_class = bulk_module_config[module]
    # Create chunks of data for processing later
    module_service = module_service_class(bulk_id=import_temp_id, jwt_token=jwt_token, client_id=client_id,
                                          user_id=user_id)
    module_service.create_bulk_process_chunks()
    # Processing bulk edit
    data_info = {
        'module': module,
        'import_temp_id': str(import_temp_id),
        'jwt_token': jwt_token,
        'client_id': str(client_id),
        'user_id': str(user_id)
    }
    processing_bulk_module_chunk(**data_info)

    return f'[{self.request.id}][{module}] PF CREATE BULK PROCESS CHUNKS'
