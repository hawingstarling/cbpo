from datetime import datetime, timezone, timedelta

from app.financial.models import SaleItem, BrandSetting


class INoBrandSettings:
    client_id: str
    client_name: str
    brand_name: str

    def __init__(self, client_id, client_name, brand_name):
        self.client_id = client_id
        self.client_name = client_name
        self.brand_name = brand_name


def alert_no_brand_settings(client_id: str) -> [INoBrandSettings]:
    brand_setting_query_set = BrandSetting.objects \
        .tenant_db_for(client_id) \
        .filter(client_id=client_id) \
        .all() \
        .values('client_id', 'channel_id', 'brand_id')

    a_month_ago = datetime.now(tz=timezone.utc) - timedelta(days=30)

    sale_item_query_set_grouped = SaleItem.objects \
        .tenant_db_for(client_id) \
        .select_related('sale', 'brand', 'client') \
        .filter(brand__isnull=False, brand__is_obsolete=False, created__gte=a_month_ago) \
        .values('client_id', 'sale__channel_id', 'sale__channel__name', 'brand_id', 'brand__name', 'client__name') \
        .distinct('client_id', 'sale__channel_id', 'brand_id')

    res_no_brand_settings = []

    for group_by_item in sale_item_query_set_grouped:
        try:
            find_one = filter(
                lambda ele:
                ele['client_id'] == group_by_item['client_id'] and
                ele['channel_id'] == group_by_item['sale__channel_id'] and
                ele['brand_id'] == group_by_item['brand_id'],
                brand_setting_query_set)
            next(find_one)
        except StopIteration:
            _brand_name = f"{group_by_item['brand__name']} ({group_by_item['sale__channel__name']})"
            res_no_brand_settings.append(INoBrandSettings(client_id=group_by_item['client_id'],
                                                          client_name=group_by_item['client__name'],
                                                          brand_name=_brand_name))
    return res_no_brand_settings
