import copy
import io
import json
from datetime import timedelta
from decimal import Decimal
from unittest import mock
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.jobs.event import handler_trigger_trans_event_sale_item_ws
from app.financial.jobs.sale_event import handler_trans_event_data_to_sale_level
from app.financial.jobs.sale_financial import handler_trigger_split_sale_item_financial_ws
from app.financial.jobs.time_control import handler_job_time_control_check_type_is_ready_workspace, \
    handler_time_control_process_type_is_ready_workspace
from app.financial.models import DataFlattenTrack, SaleItemTransaction, SaleStatus, Sale, SaleItem, \
    CacheSaleItemTransaction, Channel, ClientPortal, DataStatus, FulfillmentChannel, SaleItemFinancial
from app.financial.variable.job_status import LIVE_FEED_JOB, TRANS_DATA_EVENT_JOB
from app.financial.services.transaction.calculate.sale import CalculateTransSaleManage
from app.financial.services.transaction.calculate.sale_item import CalculateTransSaleItemsManage
from app.financial.jobs.time_control import handler_time_control_create_event
from app.financial.tests.base import BaseAPITest
from app.financial.tests.fixtures.trans_event import TRANS_EVENT, TRANS_EVENT_STATUS
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE
from app.core.variable.pf_trust_ac import OPEN_STATUS, FINANCIAL_EVENT_TYPE, DONE_STATUS, ERROR_STATUS
from app.financial.variable.sale_status_static_variable import (
    SALE_PENDING_STATUS, RETURN_REVERSED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS)
from app.financial.variable.transaction.config import ShipmentEvent, RefundEvent, FeeCategory, AdjustmentEvent, \
    ServiceFeeEvent, ChargeCategory, PromotionCategory, QuantityCategory
from app.financial.variable.transaction.generic import RETURN_POSTAGE_BILLING_TYPES
from app.financial.variable.transaction.type.adjustment import ReversalReimbursementType, PostageBillingPostageType
from config.settings.common import ROOT_DIR
from app.financial.variable.shipping_cost_source import AMZ_POSTAGE_BILLING_SOURCE_KEY, \
    AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY, BRAND_SETTING_SOURCE_KEY

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/sale.json",
    APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
    APPS_DIR + "financial/tests/fixtures/sale_item.json",
    APPS_DIR + "financial/tests/fixtures/client_settings.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class SaleItemTransEventTest(BaseAPITest):
    fixtures = fixtures
    type_flatten = DATA_FLATTEN_TYPE[0][0]

    def setUp(self):
        super().setUp()

        if SaleItem.objects.tenant_db_for(self.client_id).count() == 0:
            self.db_table_client(new_table=True)

        self.marketplace = 'amazon.com'

        # create table manage data sale items
        self.create_flatten_manage_sale_items()

        self.flatten = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                  type=self.type_flatten)
        self.channel_sale_ids = ["111-222-3334", "111-222-3336", "111-222-3338"]
        self.sale_item_ids = []

    def fake_ac_service_trans_event_200(self, **query_params):
        content = io.BytesIO(json.dumps(TRANS_EVENT).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_trans_event_status_200(self, **query_params):
        content = io.BytesIO(json.dumps(TRANS_EVENT_STATUS).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_trans_event_status_200_not_ready(self, **query_params):
        data = copy.deepcopy(TRANS_EVENT_STATUS)
        data.update({'ready': False})
        content = io.BytesIO(json.dumps(data).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_trans_event400(self, **query_params):
        content = {
            "statusCode": HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": "Invalid request query input"
        }
        content = io.BytesIO(json.dumps(content).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_400_BAD_REQUEST)

    def fake_ac_servicetrans_event500(self, **query_params):
        content = {
            "statusCode": HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": "Internal Server Error"
        }
        content = io.BytesIO(json.dumps(content).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch('app.core.services.ac_service.ACManager.get_financial_events', fake_ac_service_trans_event400)
    def test_job_error_ac_trans_event_400(self):
        handler_trigger_trans_event_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                 amazon_order_ids=self.channel_sale_ids)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)
        self.flatten.refresh_from_db()

        print(self.flatten.log)

        log_event = json.loads(self.flatten.log_event)

        errors = log_event.get('errors', {})
        log_errors = next(iter(errors.values()))
        print(log_errors)

        log_error = '[ACManager] __handler_result error: {"statusCode": 400, "error": "Bad Request", "message": "Invalid request query input"}'
        self.assertEqual(log_errors, log_error)

    @mock.patch('app.core.services.ac_service.ACManager.get_financial_events', fake_ac_servicetrans_event500)
    def test_job_error_ac_trans_event_500(self):
        handler_trigger_trans_event_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                 amazon_order_ids=self.channel_sale_ids)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)
        self.flatten.refresh_from_db()

        log_event = json.loads(self.flatten.log_event)

        print(log_event)

        errors = log_event.get('errors', {})
        log_errors = next(iter(errors.values()))
        print(log_errors)
        log_error = '[ACManager] __handler_result error: {"statusCode": 500, "error": "Internal Server Error", "message": "Internal Server Error"}'
        self.assertEqual(log_errors, log_error)

    def import_process_trans_event(self):
        # ---------- FulfillmentChannel is FBA -----------------------
        sale_status = SaleStatus.objects.tenant_db_for(self.client_id).get(value=SALE_PENDING_STATUS)
        Sale.objects.tenant_db_for(self.client_id).filter(channel_sale_id='111-222-3336',
                                                          channel__name='amazon.com').update(sale_status=sale_status)
        self.flatten.log_event = '{}'
        self.flatten.log = None
        self.flatten.save()
        handler_trigger_trans_event_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                 amazon_order_ids=self.channel_sale_ids)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)

        self.flatten.refresh_from_db()
        self.assertEqual(self.flatten.log, None)

        log_event = json.loads(self.flatten.log_event)

        print(log_event)

        # valid data

        query_set = SaleItemTransaction.objects.tenant_db_for(self.client_id).all()

        # for item in query_set:
        #     print(item.channel_sale_id, item.channel.name, item.sku, item.type, item.event, item.amount, item.category,
        #           item.seq)

        self.assertEqual(query_set.count(), 26)

        cache_query_set = CacheSaleItemTransaction.objects.tenant_db_for(self.client_id).all()

        self.assertEqual(cache_query_set.count(), 1)

        # event = shipment & category = fee
        shipment_fee = query_set.filter(event=ShipmentEvent, category=FeeCategory)
        self.assertEqual(shipment_fee.count(), 3)

        # event = shipment & category = promotion
        promotion_fee = query_set.filter(event=ShipmentEvent, category=PromotionCategory)
        self.assertEqual(promotion_fee.count(), 1)

        # event = refund & category = fee
        refund_fee = query_set.filter(event=RefundEvent, category=FeeCategory)
        self.assertEqual(refund_fee.count(), 4)

        # event = refund & category = fee
        refunded_quantity = query_set.filter(event=RefundEvent, category=QuantityCategory)
        self.assertEqual(refunded_quantity.count(), 2)

        # event = adjustment & type = ReversalReimbursementType
        adjustment = query_set.filter(event=AdjustmentEvent,
                                      type__in=[ReversalReimbursementType,
                                                PostageBillingPostageType] + RETURN_POSTAGE_BILLING_TYPES)
        self.assertEqual(adjustment.count(), 7)

        # event = service_fee & category = Fee
        service_fee = query_set.filter(event=ServiceFeeEvent, category=FeeCategory)
        self.assertEqual(service_fee.count(), 1)

        # event = shipment & category = charge
        shipment_charge = query_set.filter(event=ShipmentEvent, category=ChargeCategory)
        self.assertEqual(shipment_charge.count(), 5)

        # event = refund & category = charge
        refund_charge = query_set.filter(event=RefundEvent, category=ChargeCategory)
        self.assertEqual(refund_charge.count(), 3)

        channel = Channel.objects.tenant_db_for(self.client_id).get(name__iexact='amazon.com')

        client = ClientPortal.objects.tenant_db_for(self.client_id).get(id=self.client_id)

        # validate data model transaction

        filters = {
            'channel_sale_id': '111-222-3336',
            'channel': channel
        }
        sale = Sale.objects.tenant_db_for(self.client_id).get(**filters)
        item = sale.saleitem_set.tenant_db_for(sale.client_id).get(sku='AL-DAT-2236')

        fulfillment_type = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name__iexact='FBA')
        item.fulfillment_type = fulfillment_type
        item.save()

        #
        cal_sale_item = CalculateTransSaleItemsManage(client_id=self.client_id, job_action=TRANS_DATA_EVENT_JOB,
                                                      instance=item)
        trans_event_data = cal_sale_item.process()

        print(f"info trans event calculate FBA : {trans_event_data}")

        self.assertEqual(trans_event_data['channel_listing_fee'], Decimal('0.00'))

        self.assertEqual(Decimal(trans_event_data['other_channel_fees']), Decimal("16.61"))
        self.assertEqual(Decimal(trans_event_data['reimbursement_costs']), Decimal("68.76"))
        self.assertEqual(Decimal(trans_event_data['refund_admin_fee']), Decimal("2.67"))

        # tax_charged calculate service
        self.assertEqual(trans_event_data['tax_charged'], Decimal('7.7'))

        # shipping_cost calculate service ( with FBA fulfillment type)
        self.assertEqual(trans_event_data['actual_shipping_cost'], Decimal('2.00'))
        self.assertEqual(trans_event_data['shipping_cost_source'], AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY)
        self.assertEqual(trans_event_data['shipping_cost_accuracy'], 100)
        self.assertEqual(trans_event_data.get('return_postage_billing'), None)

        self.assertEqual(trans_event_data['channel_tax_withheld'], Decimal('0.00'))
        self.assertEqual(trans_event_data['channel_tax_withheld_accuracy'], 100)

        self.assertEqual(trans_event_data['total_financial_amount'], Decimal('55.18'))

        self.assertEqual(trans_event_data['refunded_quantity'], 1)

        self.assertEqual(trans_event_data['financial_dirty'], True)

        # verify item has update
        item.refresh_from_db()

        self.assertEqual(item.channel_listing_fee, Decimal('0.00'))
        self.assertEqual(item.channel_listing_fee_accuracy, 100)

        self.assertEqual(item.other_channel_fees, Decimal('16.61'))
        self.assertEqual(item.reimbursement_costs, Decimal('68.76'))
        self.assertEqual(item.refund_admin_fee, Decimal('2.67'))
        self.assertEqual(item.tax_charged, Decimal('7.7'))
        self.assertEqual(item.shipping_cost, Decimal('2.00'))
        self.assertEqual(item.shipping_cost_source, AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY)
        self.assertEqual(item.shipping_cost_accuracy, 100)
        self.assertEqual(item.return_postage_billing, None)

        self.assertEqual(item.channel_tax_withheld, Decimal('0.00'))
        self.assertEqual(item.channel_tax_withheld_accuracy, 100)

        self.assertEqual(item.total_financial_amount, Decimal('55.18'))

        # check exist records financial
        handler_trigger_split_sale_item_financial_ws(client_id=self.client_id, marketplace=self.marketplace)
        financial_queryset = SaleItemFinancial.objects.tenant_db_for(self.client_id).filter(sale_item_id=item.pk)
        self.assertEqual(financial_queryset.count() > 0, True)

        # validate sale item cancelled

        data_verify = {
            'item_profit': Decimal('55.18'),
            'item_margin': None
        }

        self.__validate_sale_item_cancelled(item, data_verify)

        # ------------ FulfillmentChannel MFN -----------------

        fulfillment_type = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name__iexact='MFN')
        item.fulfillment_type = fulfillment_type
        item.save()

        #
        sale.refresh_from_db()
        print(f"Is Prime MFN : {sale.is_prime}")

        cal_sale_item = CalculateTransSaleItemsManage(client_id=self.client_id, job_action=TRANS_DATA_EVENT_JOB,
                                                      instance=item)
        trans_event_data = cal_sale_item.process()

        print(f"info trans event calculate MFN : {trans_event_data}")

        self.assertEqual(trans_event_data['other_channel_fees'], Decimal('16.61'))
        self.assertEqual(Decimal(trans_event_data['reimbursement_costs']), Decimal("68.76"))
        self.assertEqual(Decimal(trans_event_data['refund_admin_fee']), Decimal("2.67"))

        # shipping_cost calculate service ( with MFN fulfillment type)
        self.assertEqual(trans_event_data['estimated_shipping_cost'], Decimal('16.28'))
        self.assertEqual(trans_event_data['shipping_cost_source'], AMZ_POSTAGE_BILLING_SOURCE_KEY)
        self.assertEqual(trans_event_data['shipping_cost_accuracy'], 75)
        self.assertEqual(trans_event_data['return_postage_billing'], Decimal('3.51'))

        self.assertEqual(item.channel_tax_withheld, Decimal('0.00'))
        self.assertEqual(item.channel_tax_withheld_accuracy, 100)

        self.assertEqual(trans_event_data['total_financial_amount'], Decimal('37.39'))

        self.assertEqual(trans_event_data['financial_dirty'], True)

        # trigger job for implement update sale item db
        Sale.objects.tenant_db_for(self.client_id).filter(channel_sale_id='111-222-3336',
                                                          channel__name='amazon.com').update(sale_status=sale_status)
        self.flatten.log_event = '{}'
        self.flatten.log = None
        self.flatten.save()

        item.shipping_cost_accuracy = 50
        item.estimated_shipping_cost = 2.0
        item.actual_shipping_cost = None
        item.shipping_cost = 2.0
        item.save()

        handler_trigger_trans_event_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                 amazon_order_ids=self.channel_sale_ids)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)

        # verify item has update
        item.refresh_from_db()

        self.assertEqual(item.channel_listing_fee, Decimal('0.00'))
        self.assertEqual(item.channel_listing_fee_accuracy, 100)
        self.assertEqual(item.other_channel_fees, Decimal('16.61'))
        self.assertEqual(item.reimbursement_costs, Decimal('68.76'))
        self.assertEqual(item.refund_admin_fee, Decimal('2.67'))
        self.assertEqual(item.tax_charged, Decimal('7.7'))
        self.assertEqual(item.shipping_cost, Decimal('16.28'))
        self.assertEqual(item.shipping_cost_source, AMZ_POSTAGE_BILLING_SOURCE_KEY)
        self.assertEqual(item.shipping_cost_accuracy, 75)
        self.assertEqual(item.return_postage_billing, Decimal('3.51'))

        self.assertEqual(item.channel_tax_withheld, Decimal('0.00'))
        self.assertEqual(item.channel_tax_withheld_accuracy, 100)

        self.assertEqual(item.total_financial_amount, Decimal('37.39'))

        self.assertEqual(financial_queryset.count() > 0, True)

        data_verify = {
            'item_profit': Decimal('37.39'),
            'item_margin': None
        }

        self.__validate_sale_item_cancelled(item, data_verify)

        # ----------- Verify trans event chang status sale & sale items ------------------
        self.__verify_sale_change_status(sale)

    def __validate_sale_item_cancelled(self, item, data_verify):
        sale_status_origin = item.sale_status

        # change sale to cancelled

        cancelled = SaleStatus.objects.tenant_db_for(self.client_id).get(name='Cancelled')
        item.sale_status = cancelled
        item.save()

        flat_sale_items_bulks_sync_task(client_id=self.client_id)

        self.sale_item_ids = [item.pk]

        rs = self.get_result_flatten_data()

        print(rs)

        item_ds = rs[0]

        self.assertEqual(item_ds['item_profit'], data_verify['item_profit'])
        self.assertEqual(item_ds['item_margin'], data_verify['item_margin'])

        self.sale_item_ids = []
        item.sale_status = sale_status_origin
        item.save()

    def __verify_sale_change_status(self, sale):
        # reset sale status
        sale_status_pending = SaleStatus.objects.tenant_db_for(self.client_id).get(value=SALE_PENDING_STATUS)
        sale.sale_status = sale_status_pending
        sale.save()
        sale.saleitem_set.tenant_db_for(sale.client_id).all().update(sale_status=sale_status_pending)

        # test update trans vent data to sale level and sale items level , status = Return Reversed
        trans_value = CalculateTransSaleManage(client_id=self.client_id, job_action=LIVE_FEED_JOB,
                                               instance=sale).process()

        print('trans value of sale : {}'.format(trans_value))

        self.assertEqual(trans_value['sale_status'].value, RETURN_REVERSED_STATUS)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)

        sale.refresh_from_db()

        self.assertEqual(sale.sale_status, trans_value['sale_status'])

        item_query_set = SaleItem.objects.tenant_db_for(self.client_id).filter(sale=sale,
                                                                               sale_status=trans_value['sale_status'])

        self.assertEqual(item_query_set.count(), 1)

        item = item_query_set.filter(sku='AL-DAT-2236').first()

        self.assertEqual(item.sale_status, trans_value['sale_status'])

        # remove event = AdjustmentEvent for test Partially Refunded
        quantity_origin = item.quantity

        item.quantity = 2
        item.save()

        SaleItemTransaction.objects.tenant_db_for(self.client_id).filter(event=AdjustmentEvent).delete()

        partially_refunded = SaleStatus.objects.tenant_db_for(self.client_id).get(value=SALE_PARTIALLY_REFUNDED_STATUS)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)

        sale.refresh_from_db()

        self.assertEqual(sale.sale_status, partially_refunded)

        item.refresh_from_db()

        self.assertEqual(item.sale_status, partially_refunded)

        item.quantity = quantity_origin
        item.save()

    @mock.patch('app.core.services.ac_service.ACManager.get_financial_events', fake_ac_service_trans_event_200)
    def test_job_sync_flatten_trans_event_200(self):
        SaleItem.objects.tenant_db_for(self.client_id).filter(sale_id=3000001) \
            .update(shipping_cost=8, actual_shipping_cost=None, estimated_shipping_cost=8, shipping_cost_accuracy=80,
                    shipping_cost_source=BRAND_SETTING_SOURCE_KEY)
        self.import_process_trans_event()

        channel = Channel.objects.tenant_db_for(self.client_id).get(name__iexact='amazon.com')

        filters = {
            'client_id': self.client_id,
            'channel_sale_id': '111-222-3336',
            'channel_id': channel.pk
        }
        sale = Sale.objects.tenant_db_for(self.client_id).get(**filters)

        self.__calculate_prime_mfn(sale)

    def __calculate_prime_mfn(self, sale):
        fulfillment_type = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name='MFN')
        sale.is_prime = True
        sale.save()

        # 2 items split calculate
        shipping_cost_target = Decimal('8.14')
        sku_calculate = ['AL-DAT-2236', 'AL-DAT-3237']
        self.__verify_cal_prime_mfn(sale, fulfillment_type, sku_calculate, shipping_cost_target)

        # 3 items with 2 items calculated before
        sale.saleitem_set.tenant_db_for(sale.client_id).filter(sku__in=['AL-DAT-2236', 'AL-DAT-3237']).update(
            shipping_cost=2.72,
            actual_shipping_cost=2.72,
            shipping_cost_accuracy=100,
            fulfillment_type=fulfillment_type)
        sku_calculate = ['AL-DAT-3238']
        shipping_cost_target = Decimal('8.74')
        transaction.on_commit(
            lambda: self.__verify_cal_prime_mfn(sale, fulfillment_type, sku_calculate, shipping_cost_target))

        # 1 items
        sale.saleitem_set.tenant_db_for(sale.client_id).filter(sku__in=['AL-DAT-2236', 'AL-DAT-3237']).delete()
        sku_calculate = ['AL-DAT-2236']
        shipping_cost_target = Decimal('8.14')
        transaction.on_commit(
            lambda: self.__verify_cal_prime_mfn(sale, fulfillment_type, sku_calculate, shipping_cost_target))

    def __verify_cal_prime_mfn(self, sale, fulfillment_type, sku_calculate, shipping_cost_target):
        # update for compared hash changed
        CacheSaleItemTransaction.objects.tenant_db_for(self.client_id).filter(
            channel_sale_id=sale.channel_sale_id).update(hash='AAAAAA')

        # reset data sale items for update
        queryset = sale.saleitem_set.tenant_db_for(self.client_id).filter(sku__in=sku_calculate)
        queryset.update(shipping_cost=1, actual_shipping_cost=None, estimated_shipping_cost=1,
                        shipping_cost_accuracy=70,
                        fulfillment_type=fulfillment_type)

        # reset log entry for update
        self.flatten.log_event = '{}'
        self.flatten.log = None
        self.flatten.save()

        # action update
        handler_trigger_trans_event_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                 amazon_order_ids=self.channel_sale_ids)
        handler_trans_event_data_to_sale_level(client_id=self.client_id, marketplace=self.marketplace,
                                               amazon_order_ids=self.channel_sale_ids)

        print(f"items total : {queryset.count()}")

        for item in queryset:
            self.assertEqual(item.shipping_cost, shipping_cost_target)
            self.assertEqual(item.shipping_cost_source, AMZ_POSTAGE_BILLING_SOURCE_KEY)
            self.assertEqual(item.shipping_cost_accuracy, 75)

    @mock.patch('app.core.services.ac_service.ACManager.get_financial_events', fake_ac_service_trans_event_200)
    def test_job_sync_flatten_trans_event_with_tracking(self):
        # create data status tracking event
        datetime_type = timezone.now() - timedelta(days=1)
        handler_time_control_create_event(self.client_id, datetime_type.date())

        sale_status = SaleStatus.objects.tenant_db_for(self.client_id).get(value=SALE_PENDING_STATUS)
        Sale.objects.tenant_db_for(self.client_id).filter(channel_sale_id='111-222-3336',
                                                          channel__name='amazon.com').update(sale_status=sale_status)
        self.flatten.log_event = '{}'
        self.flatten.log = None
        self.flatten.save()

        channel = Channel.objects.tenant_db_for(self.client_id).get(name__iexact='amazon.com')

        data_status = DataStatus.objects.tenant_db_for(self.client_id).get(client_id=self.client_id, channel=channel,
                                                                           type=FINANCIAL_EVENT_TYPE,
                                                                           date=datetime_type.date())

        self.assertEqual(data_status.status, OPEN_STATUS)

        with mock.patch('app.core.services.ac_service.ACManager.get_financial_events_status',
                        self.fake_ac_service_trans_event_status_200_not_ready):
            handler_job_time_control_check_type_is_ready_workspace(self.client_id)

            data_status.refresh_from_db()

            print(data_status.log)

            log = json.loads(data_status.log)

            print(log)

            self.assertEqual(log['status'], f'Data status is not ready')

            self.assertEqual(data_status.status, ERROR_STATUS)

        SaleItem.objects.tenant_db_for(self.client_id).filter(sale_id=3000001) \
            .update(shipping_cost=8, actual_shipping_cost=None, estimated_shipping_cost=8, shipping_cost_accuracy=80,
                    shipping_cost_source=BRAND_SETTING_SOURCE_KEY)
        with mock.patch('app.core.services.ac_service.ACManager.get_financial_events_status',
                        self.fake_ac_service_trans_event_status_200):
            handler_job_time_control_check_type_is_ready_workspace(self.client_id)
            handler_time_control_process_type_is_ready_workspace(client_id=self.client_id,
                                                                 data_status_id=data_status.pk)
            self.import_process_trans_event()

            data_status.refresh_from_db()

            log = json.loads(data_status.log)

            self.assertEqual(log['status'], 'Success')

            self.assertEqual(data_status.status, DONE_STATUS)
