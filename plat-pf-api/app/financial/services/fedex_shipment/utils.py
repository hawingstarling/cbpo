import maya
from django.db.models import Q, Count, Case, F, When, Value, CharField, Func, BigIntegerField
from django.db.models.functions import Cast

from app.financial.models import FedExShipment, ShippingInvoice
from app.financial.services.fedex_shipment.config import config_fedex_shipment_search, FEDEX_SHIPMENT_ONE, \
    SHIPPING_INVOICE_DONE, SHIPPING_INVOICE_DONE_WITH_ERRORS, SHIPPING_INVOICE_PENDING, config_shipping_invoice_search, \
    FEDEX_SHIPMENT_COMPLETED
from app.financial.services.postgres_fulltext_search import PostgresFulltextSearch, ISortConfigPostgresFulltextSearch


def get_query_set_filter_shipping_invoice(client_id: str, ids: list = [], from_date: str = None, to_date: str = None,
                                          status: str = None, source: str = None, sort_field: str = None,
                                          sort_direction: str = None, keyword: str = None):
    sort_config = []
    if sort_field:
        if sort_field in ['total_transactions', 'matched_transactions', 'unmatched_transactions',
                          'matching_status', 'matched_sales', 'invoice_balances', 'matched_time', 'source_files']:
            sort_field = 'invoice_date'
        sort_config = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
    #
    queryset = ShippingInvoice.objects.tenant_db_for(client_id).filter(client_id=client_id)
    if ids:
        queryset = queryset.filter(pk__in=ids)
    else:
        cond = Q()
        if status or source:
            queryset_trans = FedExShipment.objects.tenant_db_for(client_id).filter(client_id=client_id)
            if source:
                queryset_trans = queryset_trans.filter(source__icontains=source)
            if status:
                queryset_trans = queryset_trans.values('shipping_invoice__id') \
                    .annotate(
                    total_transactions=Count('pk'),
                    matched_transactions=Count('pk',
                                               filter=Q(status__in=[FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_COMPLETED])),
                    unmatched_transactions=F('total_transactions') - F('matched_transactions'),
                    matching_status=Case(
                        When(total_transactions=F('matched_transactions'), then=Value(SHIPPING_INVOICE_DONE)),
                        When(unmatched_transactions__gt=0, matched_transactions__gt=0,
                             then=Value(SHIPPING_INVOICE_DONE_WITH_ERRORS)),
                        default=Value(SHIPPING_INVOICE_PENDING),
                        output_field=CharField()
                    )
                )
                queryset_trans = queryset_trans.filter(matching_status=status)
            #
            ids = queryset_trans.values_list('shipping_invoice__id', flat=True)
            cond.add(Q(pk__in=ids), Q.AND)
        #
        if from_date:
            from_date = maya.parse(from_date).datetime().date()
            cond.add(Q(invoice_date__gte=from_date), Q.AND)
        #
        if to_date:
            to_date = maya.parse(to_date).datetime().date()
            cond.add(Q(invoice_date__lte=to_date), Q.AND)
        #
        queryset = queryset.filter(cond)
        #
        if keyword:
            queryset = PostgresFulltextSearch(
                model_objects_manager=queryset,
                fields_config=config_shipping_invoice_search,
                sort_config=sort_config).search_rank_on_contain(keyword)
            return queryset
    if sort_config:
        order_by = [item.output_str_sorting for item in sort_config]
        queryset = queryset.order_by(*order_by)
    return queryset


def get_query_set_filter_shipping_invoice_transaction(client_id: str, ids: list = [], status: str = None,
                                                      shipping_invoice_id: str = None, source: str = None,
                                                      sort_field: str = None, sort_direction: str = None,
                                                      keyword: str = None):
    sort_config = []
    if sort_field:
        if sort_field == 'transaction_id':
            sort_field = 'trans_id'
        sort_config = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
    #
    queryset = FedExShipment.objects.tenant_db_for(client_id).filter(client_id=client_id).annotate(
        trans_id=Cast('transaction_id', BigIntegerField()))
    if ids:
        queryset = queryset.filter(pk__in=ids)
    else:
        cond = Q()
        if shipping_invoice_id:
            cond.add(Q(shipping_invoice_id=shipping_invoice_id), Q.AND)
        if status:
            cond.add(Q(status=status), Q.AND)
        if source:
            cond.add(Q(source__icontains=source), Q.AND)
        #
        queryset = queryset.filter(cond)
        if keyword:
            queryset = PostgresFulltextSearch(
                model_objects_manager=queryset,
                fields_config=config_fedex_shipment_search,
                sort_config=sort_config).search_rank_on_contain(keyword)
            return queryset
    if sort_config:
        order_by = [item.output_str_sorting for item in sort_config]
        queryset = queryset.order_by(*order_by)
    return queryset


def get_shipping_invoice_trans_matched_sales_ids(client_id: str, shipping_invoice_id: str = None):
    cond = Q(client_id=client_id, shipping_invoice_id=shipping_invoice_id,
             status__in=[FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_COMPLETED])
    sale_ids = FedExShipment.objects.tenant_db_for(client_id).filter(cond) \
        .annotate(sale_ids=Func(F('matched_sales'), function='unnest')) \
        .values_list('sale_ids', flat=True).distinct()
    return list(sale_ids)
