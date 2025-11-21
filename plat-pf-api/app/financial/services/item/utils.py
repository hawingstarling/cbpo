from django.db.models import Q

from app.financial.models import Item
from app.financial.services.item.config import config_shipping_items_search
from app.financial.services.postgres_fulltext_search import PostgresFulltextSearch, ISortConfigPostgresFulltextSearch


def get_query_set_filter_items(client_id: str, ids: list = [], sort_field: str = None, channel: str = None,
                               brand: str = None, sort_direction: str = None, keyword: str = None, **kwargs):
    sort_config = []
    if sort_field:
        sort_config = [ISortConfigPostgresFulltextSearch(
            field_name=sort_field, direction=sort_direction)]
    #
    queryset = Item.objects.tenant_db_for(
        client_id).filter(client_id=client_id)
    if ids:
        queryset = queryset.filter(pk__in=ids)
    else:
        cond = Q()
        if channel:
            cond.add(Q(channel__name=channel), Q.AND)
        if brand:
            cond.add(Q(brand__name=brand), Q.AND)
        #
        queryset = queryset.filter(cond)
        #
        if keyword:
            queryset = PostgresFulltextSearch(
                model_objects_manager=queryset,
                fields_config=config_shipping_items_search,
                sort_config=sort_config).search_rank_on_contain(keyword)
            return queryset
    if sort_config:
        order_by = [item.output_str_sorting for item in sort_config]
        queryset = queryset.order_by(*order_by)
    return queryset
