import logging
from django.db.models import Q
from celery import current_app
from app.financial.models import AutoFeedBrand, DataFlattenTrack, Channel
from app.financial.services.feeds.sale_item_data_feed import SaleItemDataFeed
from app.financial.services.feeds.yoy_30d_sales_feed import YOYSaleDataFeed
from app.financial.services.integrations.advertising import AdvertisingManager
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_YOY_30_DAY_SALE_KEY

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def handler_auto_generate_sale_items_data_feed(self, client_id: any, **kwargs):
    logger.info(f"[{self.request.id}][{client_id}][handler_auto_generate_sale_items_data_feed] begin processing ... ")
    cond = Q(client_id=client_id)
    if 'auto_feed_ids' in kwargs:
        cond &= Q(pk__in=kwargs.pop('auto_feed_ids'))
    if 'brand_ids' in kwargs:
        cond &= Q(brand_id__in=kwargs.pop('brand_ids'))
    if 'channel_ids' in kwargs:
        channel_ids = Channel.objects.tenant_db_for(client_id).filter(pk__in=kwargs.pop('channel_ids')).values_list(
            'pk',
            flat=True)
    else:
        channel_ids = Channel.objects.tenant_db_for(client_id).values_list('pk', flat=True)
    channel_ids = list(channel_ids)
    queryset = AutoFeedBrand.objects.tenant_db_for(client_id).filter(cond).all()
    for auto_feed in queryset.iterator():
        client_id = str(auto_feed.client.id)
        if auto_feed.channel and auto_feed.channel.pk in channel_ids:
            data_feed_handler = SaleItemDataFeed(client_id, channel=auto_feed.channel,
                                                 brand=auto_feed.brand, **kwargs)
            data_feed_handler.generate()
        else:
            for channel_id in channel_ids:
                data_feed_handler = SaleItemDataFeed(client_id, brand=auto_feed.brand, channel_id=channel_id, **kwargs)
                data_feed_handler.generate()
    SaleItemDataFeed.remove_by(client_id=client_id, latest=False, type=FLATTEN_SALE_ITEM_KEY)


@current_app.task(bind=True)
def handler_auto_generate_yoy_30d_sales_data_feed(self, client_id: any, **kwargs):
    logger.info(
        f"[{self.request.id}][{client_id}][handler_auto_generate_yoy_30d_sales_data_feed] begin processing ... ")
    cond = Q(client_id=client_id)
    if 'auto_feed_ids' in kwargs:
        cond &= Q(pk__in=kwargs.pop('auto_feed_ids'))
    if 'brand_ids' in kwargs:
        cond &= Q(brand_id__in=kwargs.pop('brand_ids'))
    if 'channel_ids' in kwargs:
        channel_ids = Channel.objects.tenant_db_for(client_id).filter(pk__in=kwargs.pop('channel_ids')).values_list(
            'pk',
            flat=True)
    else:
        channel_ids = Channel.objects.tenant_db_for(client_id).values_list('pk', flat=True)
    channel_ids = list(channel_ids)
    queryset = AutoFeedBrand.objects.tenant_db_for(client_id).filter(cond).all()
    for auto_feed in queryset.iterator():
        client_id = str(auto_feed.client.id)
        if auto_feed.channel and auto_feed.channel.pk in channel_ids:
            data_feed_handler = YOYSaleDataFeed(client_id, channel=auto_feed.channel, brand=auto_feed.brand, **kwargs)
            data_feed_handler.generate()
        else:
            for channel_id in channel_ids:
                data_feed_handler = YOYSaleDataFeed(client_id, brand=auto_feed.brand, channel_id=channel_id, **kwargs)
                data_feed_handler.generate()
    YOYSaleDataFeed.remove_by(client_id=client_id, latest=False, type=FLATTEN_YOY_30_DAY_SALE_KEY)


@current_app.task(bind=True)
def handler_sync_ac_ad_spend_information(self, client_id):
    logger.info(f"[{self.request.id}][{client_id}][sync_ac_ad_spend_information] begin processing ... ")
    cond = Q(client_id=client_id, live_feed=True, type=FLATTEN_SALE_ITEM_KEY, client__active=True) \
           & (Q(client__clientsettings__ac_mws_enabled=True) | Q(client__clientsettings__ac_spapi_enabled=True))
    flattens = DataFlattenTrack.objects.tenant_db_for(client_id).filter(cond)
    if len(flattens) == 0:
        logger.info(f"[Tasks][sync_ac_ad_spend_information] Not found flattens!")
    for flatten in flattens:
        logger.info(f"[Tasks][sync_ac_ad_spend_information] STARTED")
        ad_manager = AdvertisingManager(client_id=client_id, flatten=flatten)
        ad_manager.progress()
