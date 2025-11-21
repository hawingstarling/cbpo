import copy, io, json, time
from datetime import timedelta
from unittest import mock
from django.http import HttpResponse
from django.utils import timezone
from app.financial.jobs.time_control import handler_job_time_control_check_type_is_ready_workspace, \
    handler_time_control_process_type_is_ready_workspace
from app.financial.models import DataFlattenTrack, DataStatus, Channel, SaleItem
from app.financial.jobs.live_feed import handler_trigger_live_feed_sale_item_ws
from app.financial.tasks import handler_time_control_create_event
from app.financial.tests.base import BaseAPITest
from app.financial.tests.fixtures.sale_items_live_feed import LIVE_FEED_STATUS, SC_LIVE_FEED_AMAZON_US, \
    get_data_fake_live_feed_marketplace
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE
from app.core.variable.pf_trust_ac import SALE_EVENT_TYPE, DONE_STATUS, ERROR_STATUS, OPEN_STATUS
from app.financial.variable.shipping_cost_source import AMZ_SELLER_CENTRAL_SOURCE_KEY, AMZ_POSTAGE_BILLING_SOURCE_KEY, \
    AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY
from config.settings.common import ROOT_DIR
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

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
    APPS_DIR + "financial/tests/fixtures/generic_transaction.json",
    APPS_DIR + "financial/tests/fixtures/client_settings.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class SaleItemLiveFeedTest(BaseAPITest):
    fixtures = fixtures
    type_flatten = DATA_FLATTEN_TYPE[0][0]

    def setUp(self):
        super().setUp()

        self.marketplace = 'amazon.com'

        # create table manage data sale items
        self.create_flatten_manage_sale_items()

        self.flatten = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                  type=self.type_flatten)
        self.sale_item_ids = []

    def fake_ac_service_live_feed_200(self, **query_params):
        content = io.BytesIO(json.dumps(SC_LIVE_FEED_AMAZON_US).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_live_feed_status_200(self, **query_params):
        content = io.BytesIO(json.dumps(LIVE_FEED_STATUS).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_live_feed_not_ready(self, **query_params):
        data = copy.deepcopy(LIVE_FEED_STATUS)
        data.update({'ready': False})
        content = io.BytesIO(json.dumps(data).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def fake_ac_service_live_feed_400(self, **query_params):
        content = {
            "statusCode": HTTP_400_BAD_REQUEST,
            "error": "Bad Request",
            "message": "Invalid request query input"
        }
        content = io.BytesIO(json.dumps(content).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_400_BAD_REQUEST)

    def fake_ac_service_live_feed_500(self, **query_params):
        content = {
            "statusCode": HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Internal Server Error",
            "message": "Internal Server Error"
        }
        content = io.BytesIO(json.dumps(content).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch('app.core.services.ac_service.ACManager.get_sale_items', fake_ac_service_live_feed_400)
    def test_job_error_ac_live_feed_400_amazon_us(self):
        marketplace = 'amazon.com'
        handler_trigger_live_feed_sale_item_ws(client_id=self.client_id, marketplace=marketplace, track_logs=True)
        self.flatten.refresh_from_db()
        print(self.flatten.log)

        log_feed = json.loads(self.flatten.log_feed)

        errors = log_feed.get('errors', {})
        log_errors = next(iter(errors.values()))
        print(log_errors)

        log_error = '[ACManager] __handler_result error: {"statusCode": 400, "error": "Bad Request", "message": "Invalid request query input"}'
        self.assertEqual(log_errors, log_error)

    @mock.patch('app.core.services.ac_service.ACManager.get_sale_items', fake_ac_service_live_feed_500)
    def test_job_error_ac_live_feed_500_amazon_us(self):
        marketplace = 'amazon.com'
        handler_trigger_live_feed_sale_item_ws(client_id=self.client_id, marketplace=marketplace, track_logs=True)
        self.flatten.refresh_from_db()

        log_feed = json.loads(self.flatten.log_feed)

        print(log_feed)

        errors = log_feed.get('errors', {})
        log_errors = next(iter(errors.values()))
        print(log_errors)
        log_error = '[ACManager] __handler_result error: {"statusCode": 500, "error": "Internal Server Error", "message": "Internal Server Error"}'
        self.assertEqual(log_errors, log_error)

    @mock.patch('app.core.services.ac_service.ACManager.get_sale_items', fake_ac_service_live_feed_200)
    def test_job_sync_flatten_live_feed_200_amazon_us(self):
        self.flatten.log_feed = '{}'
        self.flatten.log = None
        self.flatten.save()
        handler_trigger_live_feed_sale_item_ws(client_id=self.client_id, marketplace='amazon.com', track_logs=True)
        self.flatten.refresh_from_db()
        self.assertEqual(self.flatten.log, None)

        log_feed = json.loads(self.flatten.log_feed)

        print(log_feed)

        errors = log_feed.get('errors', {})
        log_errors = next(iter(errors.values()))
        print(log_errors)
        self.assertEqual(len(log_errors) == 2, True)

        success = log_feed.get('success', [])
        log_success = next(iter(success.values()))
        self.assertEqual(len(log_success) == 2, True)

        self.sale_item_ids = log_success

        rs = self.get_result_flatten_data()
        self.assertEqual(len(rs), 2)

        self.compare_sale_item_update_ds(rs)
        self.verify_log_entry(2, 1)

        sale_items_live_feed = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids)
        for item in sale_items_live_feed:
            print(item.sale.channel_sale_id)
            print(item.sku)
            if item.fulfillment_type.name == 'FBA':
                self.assertEqual(item.shipping_cost_accuracy, 100)
            self.assertEqual(item.channel_listing_fee_accuracy, 80)
            self.assertEqual(item.sale_charged_accuracy, 80)
            self.assertEqual(item.tracking_fedex_id, '1234567890')
            self.assertEqual(item.label_cost, 1.0)

            # validate sale ship address
            self.assertEqual(item.sale.city, "Inyo County")
            self.assertEqual(item.sale.country, "United States")
            self.assertEqual(item.sale.postal_code, "11111-2222")
            self.assertEqual(item.sale.is_prime, True)
            #
            self.assertEqual(item.sale.customer_name, "Test")
            self.assertEqual(item.sale.recipient_name, "TestTest")
            self.assertEqual(item.sale.address_line_1, "123 Main St")
            self.assertEqual(item.sale.address_line_2, None)
            self.assertEqual(item.sale.address_line_3, None)

    def fake_ac_service_live_feed_marketplace(self, **query_params):
        data = get_data_fake_live_feed_marketplace(marketplace=self.marketplace)
        content = io.BytesIO(json.dumps(data).encode("utf-8"))
        return HttpResponse(content=content, status=HTTP_200_OK)

    def test_sync_flatten_live_feed_all_marketplace(self):
        channels = Channel.objects.tenant_db_for(self.client_id).filter(is_pull_data=True)
        for channel in channels:
            self.marketplace = channel.name
            with mock.patch('app.core.services.ac_service.ACManager.get_sale_items',
                            self.fake_ac_service_live_feed_marketplace):
                self.flatten.log_feed = '{}'
                self.flatten.log = None
                self.flatten.save()
                start = time.time()
                handler_trigger_live_feed_sale_item_ws(client_id=self.client_id, marketplace=self.marketplace,
                                                       track_logs=True)
                elapsed = time.time()

                e1 = elapsed - start

                print("Time spent exec record for workspace is: %s" % e1)

                self.flatten.refresh_from_db()
                self.assertEqual(self.flatten.log, None)

                log_feed = json.loads(self.flatten.log_feed)
                print(log_feed)

                success = log_feed.get('success', [])
                log_success = next(iter(success.values()))
                self.assertEqual(len(log_success) == 5, True)

                self.sale_item_ids = log_success

                rs = self.get_result_flatten_data()
                self.assertEqual(len(rs), 5)

                self.compare_sale_item_update_ds(rs)
                self.verify_log_entry(5, 0)

                sale_items_live_feed = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=self.sale_item_ids)
                for item in sale_items_live_feed:
                    if item.shipping_cost_source in [AMZ_SELLER_CENTRAL_SOURCE_KEY, AMZ_POSTAGE_BILLING_SOURCE_KEY]:
                        self.assertEqual(item.shipping_cost_accuracy, 75)
                    elif item.shipping_cost_source in [AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY]:
                        self.assertEqual(item.shipping_cost_accuracy, 100)
                    else:
                        pass
                    self.assertEqual(item.channel_listing_fee_accuracy, 80)
                    self.assertEqual(item.sale_charged_accuracy, 100)
                    self.assertEqual(item.tracking_fedex_id, '1234567890')

                    # validate sale ship address
                    self.assertEqual(item.sale.city, "Inyo County")
                    self.assertEqual(item.sale.country, "United States")
                    self.assertEqual(item.sale.postal_code, "11111-2222")
                    #
                    self.assertEqual(item.sale.customer_name, "Test")
                    self.assertEqual(item.sale.recipient_name, "TestTest")
                    self.assertEqual(item.sale.address_line_1, "123 Main St")
                    self.assertEqual(item.sale.address_line_2, None)
                    self.assertEqual(item.sale.address_line_3, None)

    @mock.patch('app.core.services.ac_service.ACManager.get_sale_items', fake_ac_service_live_feed_200)
    def test_job_sync_flatten_trans_event_with_tracking_amazon_us(self):
        datetime_type = timezone.now() - timedelta(days=1)
        handler_time_control_create_event(self.client_id, datetime_type.date())

        channel = Channel.objects.tenant_db_for(self.client_id).get(name__iexact='amazon.com')

        data_status = DataStatus.objects.tenant_db_for(self.client_id).get(client_id=self.client_id, channel=channel,
                                                                           type=SALE_EVENT_TYPE,
                                                                           date=datetime_type.date())

        self.assertEqual(data_status.status, OPEN_STATUS)

        with mock.patch('app.core.services.ac_service.ACManager.get_orders_status',
                        self.fake_ac_service_live_feed_not_ready):
            handler_job_time_control_check_type_is_ready_workspace(client_id=self.client_id)

            data_status.refresh_from_db()

            log = json.loads(data_status.log)

            self.assertEqual(log['status'], f'Data status is not ready')

            self.assertEqual(data_status.status, ERROR_STATUS)

        with mock.patch('app.core.services.ac_service.ACManager.get_orders_status',
                        self.fake_ac_service_live_feed_status_200):
            handler_job_time_control_check_type_is_ready_workspace(client_id=self.client_id)
            handler_time_control_process_type_is_ready_workspace(client_id=self.client_id,
                                                                 data_status_id=data_status.pk)

            data_status.refresh_from_db()

            log = json.loads(data_status.log)

            self.assertEqual(log['status'], 'Success')

            self.assertEqual(data_status.status, DONE_STATUS)
