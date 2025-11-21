from datetime import timedelta
from decimal import Decimal

from auditlog.models import LogEntry
from django.core.management.base import BaseCommand
from django.db.models import Sum, Q

from app.financial.models import FedExShipment, SaleItem, LogClientEntry
from dateutil.parser import parse
from django.core.paginator import Paginator
from django.db import transaction

from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_FEDEX
from app.database.helper import get_connection_workspace
from app.financial.services.fedex_shipment.config import FEDEX_SHIPMENT_MULTI, FEDEX_SHIPMENT_NONE, FEDEX_SHIPMENT_ONE, \
    FEDEX_SHIPMENT_PENDING
from app.financial.services.utils.common import round_currency
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_accuracy
from app.financial.variable.shipping_cost_source import FEDEX_SHIPMENT_SOURCE_KEY, AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY, \
    AMZ_POSTAGE_BILLING_SOURCE_KEY


class Command(BaseCommand):
    help = "My shiny new management command."

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
        #
        self.client_id = None
        self.client_db = None
        self.from_date = None
        self.to_date = None
        #
        self.sale_item = []
        #
        self.fedex_item_reopen = []
        #
        self.log_entries = []

        #
        self.fulfill_audit_log = False
        #
        self.re_cal_financial = False

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='client Id of workspace')
        parser.add_argument('-fd', '--from_date', type=str, help='from date compute shipment date greater than')
        parser.add_argument('-td', '--to_date', type=str, help='to date compute shipment date less than')
        #
        parser.add_argument('--re_cal_match_one', action='store_true',
                            help='re calculate match one but sale item not calculated')
        #
        parser.add_argument('--re_open_fedex', action='store_true', help='re open fedex to pending for match sale')
        parser.add_argument('-acc_gte', '--accuracy_gte', type=int,
                            help='accuracy gte filter sale item shipping cost accuracy ')
        parser.add_argument('-acc_lte', '--accuracy_lte', type=int,
                            help='accuracy lte filter sale item shipping cost accuracy')
        #
        parser.add_argument('--fulfill_audit_log', action='store_true',
                            help='Force add audit log for sale item')
        #
        parser.add_argument('--re_cal_financial', action='store_true',
                            help='Recalculate financial dirty update')

    def handle(self, *args, **options):
        print(f"------ Start execute Fedex --------")

        self.client_id = options.get('client_id')
        assert self.client_id is not None, "Pls proved client_id"

        self.client_db = get_connection_workspace(self.client_id)

        queryset = FedExShipment.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id).order_by(
            'shipment_date')

        from_date = options.get('from_date')
        to_date = options.get('to_date')
        #
        self.fulfill_audit_log = options.get('fulfill_audit_log')
        #
        self.re_cal_financial = options.get('re_cal_financial')

        if from_date and to_date:
            # check invalid format date time
            self.from_date = parse(from_date).date()
            self.to_date = parse(to_date).date()
            queryset = queryset.filter(shipment_date__gte=self.from_date, shipment_date__lte=self.to_date)

        re_open_fedex = options.get('re_open_fedex')
        if re_open_fedex:
            #
            accuracy_gte = options.get('accuracy_gte')
            accuracy_lte = options.get('accuracy_lte')
            #
            is_filter_accuracy = options.get('accuracy_gte') is not None or options.get('accuracy_lte') is not None
            #
            if accuracy_gte is None:
                accuracy_gte = 0
            if accuracy_lte is None:
                accuracy_lte = 80
            #
            self.re_open_fedex(queryset=queryset, is_filter_accuracy=is_filter_accuracy,
                               accuracy_gte=accuracy_gte, accuracy_lte=accuracy_lte)

        re_cal_match_one = options.get('re_cal_match_one')
        if re_cal_match_one:
            self.recalculate_match_one(queryset)

        print(f"------ End execute Fedex --------")

    @transaction.atomic
    def recalculate_match_one(self, queryset):
        queryset = queryset.filter(status=FEDEX_SHIPMENT_ONE)

        print(f"[{self.client_id}][recalculate_match_one] Begin recalculate match one fedex .............. ")
        print(f"[{self.client_id}][recalculate_match_one] query = {queryset.query} ")

        p = Paginator(queryset, 1000)

        num_pages = p.num_pages

        for page in range(num_pages):
            #
            page_current = page + 1

            objs = p.page(number=page_current).object_list

            length = len(objs)

            print(
                f'[{self.client_id}][recalculate_match_one] recalculate fedex page = {page_current} , count = {length} ....')
            for fedex_item in objs:
                sale_id = fedex_item.matched_sales[0]
                #
                items = SaleItem.objects.tenant_db_for(self.client_id).filter(sale_id=sale_id)
                is_amz_source = items.filter(shipping_cost_accuracy=100,
                                             shipping_cost_source__in=[AMZ_POSTAGE_BILLING_SOURCE_KEY,
                                                                       AMZ_FBA_FULFILLMENT_FEE_SOURCE_KEY]).count() > 0
                if is_amz_source:
                    fedex_item.status = FEDEX_SHIPMENT_PENDING
                    fedex_item.matched_sales = []
                    fedex_item.matched_channel_sale_ids = []
                    fedex_item.matched_time = None
                    self.fedex_item_reopen.append(fedex_item)
                    continue
                #
                count = items.count()
                #
                if count == 1:
                    item = items.first()
                    value_calculated = fedex_item.net_charge_amount
                    # print(f"[recalculate_match_one][{fedex_item.id}][{sale_id}][one] value_calculated={value_calculated}")
                    #
                    self.compared_calculate(fedex_item, item, value_calculated)
                else:
                    sum_sale_item_quantity = SaleItem.objects.tenant_db_for(self.client_id).filter(
                        sale_id=sale_id).aggregate(total=Sum('quantity'))
                    sum_sale_item_quantity = sum_sale_item_quantity['total']
                    for item in items:
                        value_calculated = (fedex_item.net_charge_amount / sum_sale_item_quantity) * item.quantity
                        value_calculated = round_currency(value_calculated)
                        # print(f"[recalculate_match_one][{fedex_item.id}][{sale_id}][multi] value_calculated={value_calculated}")
                        #
                        self.compared_calculate(fedex_item, item, value_calculated)
            if len(self.sale_item) > 0:
                print(f'[{self.client_id}][recalculate_match_one] fedex page = {page_current} , '
                      f'sale item recalculate = {self.sale_item} ....')
                SaleItem.objects.tenant_db_for(self.client_id) \
                    .bulk_update(self.sale_item, fields=['shipping_cost',
                                                         'actual_shipping_cost',
                                                         'estimated_shipping_cost',
                                                         'shipping_cost_accuracy',
                                                         'shipping_cost_source',
                                                         'dirty',
                                                         'financial_dirty', ])
            if len(self.fedex_item_reopen) > 0:
                print(f'[{self.client_id}][recalculate_match_one] fedex page = {page_current} , '
                      f'fedex item reopen = {self.fedex_item_reopen} ....')
                FedExShipment.objects.tenant_db_for(self.client_id).bulk_update(self.fedex_item_reopen,
                                                                                fields=['status', 'matched_sales',
                                                                                        'matched_channel_sale_ids',
                                                                                        'matched_time'])
            if len(self.log_entries) > 0:
                # insert log entry
                LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.log_entries,
                                                                                 ignore_conflicts=True)
            #
            self.sale_item = []
            self.fedex_item_reopen = []
            self.log_entries = []

    def compared_calculate(self, fedex_item: FedExShipment, item: SaleItem, value_calculated: any):
        #
        evaluated_accuracy = 100 if fedex_item.recipient_name else 95
        sale_item, changes = separate_shipping_cost_by_accuracy(self.client_id, item, value_calculated,
                                                    evaluated_accuracy, FEDEX_SHIPMENT_SOURCE_KEY)
        if changes:
            item.dirty = True
            item.financial_dirty = True
            self.sale_item.append(item)
        elif self.re_cal_financial:
            item.financial_dirty = True
            self.sale_item.append(item)
        #
        self.handler_fulfill_audit_log(item, changes)
        #
        if changes:
            log_entry = AuditLogCoreManager(client_id=self.client_id).set_actor_name(SYSTEM_FEDEX) \
                .create_log_entry_from_compared_changes(item, changes, action=LogEntry.Action.UPDATE)
            self.log_entries.append(log_entry)

    def handler_fulfill_audit_log(self, item, changes):
        if self.fulfill_audit_log:
            if 'shipping_cost' not in changes:
                changes.update({'shipping_cost': [None, Decimal(format(item.shipping_cost, '.2f'))]})
            if 'shipping_cost_accuracy' not in changes:
                changes.update({'shipping_cost_accuracy': [f'{0}%', f'{item.shipping_cost_accuracy}%']})
            if 'shipping_cost_source' not in changes:
                changes.update({'shipping_cost_source': [None, FEDEX_SHIPMENT_SOURCE_KEY]})

    @transaction.atomic
    def re_open_fedex(self, queryset: any, is_filter_accuracy: bool = False, accuracy_gte: int = 0,
                      accuracy_lte: int = 80):
        print(f"[{self.client_id}][re_open_fedex] Begin reopen fedex .............. ")
        if is_filter_accuracy:
            print(f"[{self.client_id}][re_open_fedex][is_filter_accuracy]: [{accuracy_gte}, {accuracy_lte}]")
            queryset = queryset.filter(status=FEDEX_SHIPMENT_MULTI)
            sale_ids = SaleItem.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id,
                                                                             shipping_cost_accuracy__gte=accuracy_gte,
                                                                             ship_date__date__gte=(
                                                                                     self.from_date - timedelta(
                                                                                 days=2)),
                                                                             ship_date__date__lte=(
                                                                                     self.to_date - timedelta(
                                                                                 days=2)),
                                                                             shipping_cost_accuracy__lte=accuracy_lte,
                                                                             shipping_cost_source=FEDEX_SHIPMENT_SOURCE_KEY).values_list(
                'sale_id',
                flat=True).distinct()
            sale_ids = list(sale_ids)
            if len(sale_ids) > 0:
                cond_match_sale = Q(matched_sales__contains=[sale_ids[0]])
                del sale_ids[0]
                for sale_id in sale_ids:
                    cond_match_sale = cond_match_sale | Q(matched_sales__contains=[sale_id])
                queryset = queryset.filter(cond_match_sale)
        else:
            queryset = queryset.filter(status__in=[FEDEX_SHIPMENT_NONE, FEDEX_SHIPMENT_MULTI])
        print(f"[{self.client_id}][re_open_fedex] queryset = {queryset.query}")
        queryset.update(status=FEDEX_SHIPMENT_PENDING, matched_sales=[], matched_channel_sale_ids=[], matched_time=None)
