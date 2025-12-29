import logging
from typing import Union
from django.db.models import Q

from app.core.utils import round_currency
from app.extensiv.models import COGSConflict
from app.extensiv.variables import EXTENSIV_COG_SOURCE, ConflictStatus, DC_COG_SOURCE
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch

logger = logging.getLogger(__name__)


def calculate_conflict_status(extensiv_cog=None, dc_cog=None, pf_cog=None):
    """
    Tính toán status conflict dựa trên tất cả các giá trị COG có sẵn.
    
    Args:
        extensiv_cog: Giá trị Extensiv COG (có thể là None)
        dc_cog: Giá trị Data Central COG (có thể là None)
        pf_cog: Giá trị PF COG (có thể là None)
    
    Returns:
        ConflictStatus: NO_CONFLICT nếu tất cả các giá trị (sau khi round) bằng nhau,
                       CONFLICT nếu có ít nhất 2 giá trị khác nhau
    """
    # Lọc bỏ các giá trị None và convert sang float
    values = []
    if extensiv_cog is not None:
        try:
            values.append(round_currency(float(extensiv_cog)))
        except (TypeError, ValueError):
            pass
    
    if dc_cog is not None:
        try:
            values.append(round_currency(float(dc_cog)))
        except (TypeError, ValueError):
            pass
    
    if pf_cog is not None:
        try:
            values.append(round_currency(float(pf_cog)))
        except (TypeError, ValueError):
            pass
    
    # Nếu không có giá trị nào hoặc chỉ có 1 giá trị, không có conflict
    if len(values) <= 1:
        return ConflictStatus.NO_CONFLICT
    
    # Kiểm tra xem tất cả các giá trị có bằng nhau không
    # Lấy giá trị đầu tiên làm chuẩn
    first_value = values[0]
    for value in values[1:]:
        if value != first_value:
            # Có ít nhất 2 giá trị khác nhau -> có conflict
            return ConflictStatus.CONFLICT
    
    # Tất cả các giá trị đều bằng nhau -> không có conflict
    return ConflictStatus.NO_CONFLICT


def init_cog_conflict(item: any, configured_priority_source: str, old_value: Union[float, None], new_value: float):
    try:
        conflict_data = {
            "client_id": item.client_id,
            "channel_id": item.sale.channel_id,
            "sku": item.sku,
            "sale_ids": [item.sale_id],
            "channel_sale_ids": [item.sale.channel_sale_id],
            "used_cog": configured_priority_source,
            "status": ConflictStatus.CONFLICT,  # Tạm thời set default, sẽ tính lại sau
            "extensiv_cog": None,
            "dc_cog": None,
            "pf_cog": None,
        }

        source_map = {
            EXTENSIV_COG_SOURCE: "extensiv_cog",
            DC_COG_SOURCE: "dc_cog"
        }

        # Set old value based on an original source
        conflict_data[source_map.get(item.cog_source, "pf_cog")] = old_value

        # Set new value based on a priority source
        conflict_data[source_map.get(
            configured_priority_source, "pf_cog")] = new_value

        # Tính lại status dựa trên tất cả các giá trị COG có sẵn
        conflict_data["status"] = calculate_conflict_status(
            extensiv_cog=conflict_data.get("extensiv_cog"),
            dc_cog=conflict_data.get("dc_cog"),
            pf_cog=conflict_data.get("pf_cog")
        )

        logger.debug(f"[init_cog_conflict] {conflict_data}")

        return COGSConflict(**conflict_data)
    except Exception as ex:
        logger.error(
            f"[{item.client_id}][pk={item.pk}][init_cog_conflict] {ex}"
        )
        return None


def get_query_set_filter_cogs_conflict(client_id: str, ids: list = [], sort_field: str = None, channel: str = None,
                                       used_cog: str = None, status: str = None, sort_direction: str = None,
                                       keyword: str = None, **kwargs):
    sort_config = []
    if sort_field:
        sort_config = [ISortConfigPostgresFulltextSearch(
            field_name=sort_field, direction=sort_direction)]
    #
    queryset = COGSConflict.objects.tenant_db_for(
        client_id).filter(client_id=client_id)
    if ids:
        queryset = queryset.filter(pk__in=ids)
    else:
        cond = Q()
        if channel:
            cond.add(Q(channel__name=channel), Q.AND)

        if used_cog:
            cond.add(Q(used_cog=used_cog), Q.AND)

        if status:
            cond.add(Q(status=status), Q.AND)

        if keyword:
            cond &= (Q(sku__icontains=keyword)
                     | Q(sale_ids__contains=[keyword])
                     | Q(note__icontains=keyword))

        if cond:
            queryset = queryset.filter(cond)

    if sort_config:
        order_by = [item.output_str_sorting for item in sort_config]
        queryset = queryset.order_by(*order_by)
    return queryset
