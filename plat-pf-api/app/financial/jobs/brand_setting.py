from datetime import datetime, timezone

from plat_import_lib_api.models import DataImportTemporary, PROCESSING

from app.core.services.authentication_service import AuthenticationService
from app.core.services.user_permission import get_user_permission
from app.financial.services.brand_settings.ship_cost_calculation_for_sale_item import BrandSettingUpdateSaleItem
from app.database.helper import get_connection_workspace
from app.financial.sub_serializers.user_serializer import UserSerializer

BRAND_SETTING_MODULE_UPDATE_SALES = 'brand_setting_update_sales'


def brand_setting_update_sale_create_bulk_progress(client_id: str,
                                                   brand_setting,
                                                   is_recalculate: bool, from_date, to_date,
                                                   jwt_token: str) -> str:
    user_id = AuthenticationService.get_user_id_jwt_token(jwt_token)
    user_permission = get_user_permission(jwt_token, client_id, user_id)
    user_info = UserSerializer(user_permission.user).data

    query_set = BrandSettingUpdateSaleItem(client_id, brand_setting, is_recalculate, from_date, to_date, None) \
        .get_sale_item_query_set()
    import_lib_bulk_progress = DataImportTemporary.objects.db_manager(using=get_connection_workspace(client_id)) \
        .create(module=BRAND_SETTING_MODULE_UPDATE_SALES, status=PROCESSING,
                meta={"ids": [str(item_id) for item_id in query_set], "client_id": client_id,
                      "user_info": user_info, "sources": ["PF Database"],
                      "command": "shipping_cost_calculation"},
                client_id=client_id, process_started=datetime.now(tz=timezone.utc),
                info_import_file={
                    "summary": {
                        "error": 0, "success": 0,
                        "total": len(query_set),
                        "errors": []},
                    "cols_file": [{"name": "id", "label": "Object ID"}],
                    "map_cols_to_module": [{"target_col": "id", "upload_col": "id"}]
                }, json_data_last_cache=[])
    return str(import_lib_bulk_progress.id)
