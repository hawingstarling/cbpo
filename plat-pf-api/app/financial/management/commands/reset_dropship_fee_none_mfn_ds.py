from decimal import Decimal

from auditlog.models import LogEntry
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db.models import Q
from dateutil.parser import parse
from app.financial.models import SaleItem, Sale, LogClientEntry
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_BRAND_SETTINGS
from app.database.helper import get_connection_workspace


class Command(BaseCommand):
    help = "Reset drop fee of item if fulfillment type is not DS."

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
        #
        self.client_id = None
        self.client_db = None
        self.marketplace = None
        self.from_date = None
        self.to_date = None
        #
        self.sale_item = []
        #
        self.log_entries = []

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='client Id of workspace')
        parser.add_argument('-mk', '--marketplace', type=str, help='channel of sale . eg: amazon.com, amazon.ca')
        parser.add_argument('-fd', '--from_date', type=str, help='from date compute shipment date greater than')
        parser.add_argument('-td', '--to_date', type=str, help='to date compute shipment date less than')

    def handle(self, *args, **options):
        print(f"------ Start execute reset Drop Fee for Is Prime Sale --------")

        self.client_id = options.get('client_id')
        assert self.client_id is not None, "Pls proved client_id"

        self.client_db = get_connection_workspace(self.client_id)

        self.marketplace = options.get('mar')

        self.marketplace = options.get('marketplace', 'amazon.com')

        cond = Q(is_prime=True, client_id=self.client_id, channel__name=self.marketplace)

        queryset = Sale.objects.tenant_db_for(self.client_id).filter(cond).order_by('date')

        from_date = options.get('from_date')
        to_date = options.get('to_date')

        if from_date and to_date:
            # check invalid format date time
            self.from_date = parse(from_date).date()
            self.to_date = parse(to_date).date()
            queryset = queryset.filter(date__date__gte=self.from_date, date__date__lte=self.to_date)

        print(f"queryset: {queryset.query}")

        p = Paginator(queryset, 1000)

        num_pages = p.num_pages

        for page in range(num_pages):
            #
            page_current = page + 1

            sale_ids = [item.id for item in p.page(number=page_current).object_list]

            length = len(sale_ids)

            print(f'[{self.client_id}] page = {page_current} , count = {length} ....')

            sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(sale_id__in=sale_ids)

            for sale_item in sale_items:
                changes = {}
                if sale_item.warehouse_processing_fee is not None and sale_item.warehouse_processing_fee > 0:
                    #
                    changes.update({'warehouse_processing_fee': [Decimal(format(sale_item.warehouse_processing_fee, '.2f')), f'{0}'],
                                    'warehouse_processing_fee_accuracy': [f'{sale_item.warehouse_processing_fee_accuracy}%', f'{0}%']})
                    #
                    sale_item.warehouse_processing_fee = 0
                    sale_item.warehouse_processing_fee_accuracy = 0
                    sale_item.dirty = True
                    sale_item.financial_dirty = True
                if changes:
                    self.sale_item.append(sale_item)
                    log_entry = AuditLogCoreManager(client_id=sale_item.client_id).set_actor_name(SYSTEM_BRAND_SETTINGS) \
                        .create_log_entry_from_compared_changes(sale_item, changes, action=LogEntry.Action.UPDATE)
                    self.log_entries.append(log_entry)

            if len(self.sale_item) > 0:
                print(
                    f'[{self.client_id}][recalculate_match_one] page = {page_current} , number reset item = {self.sale_item} ....')
                SaleItem.objects.tenant_db_for(self.client_id).bulk_update(self.sale_item, fields=['warehouse_processing_fee', 'warehouse_processing_fee_accuracy', 'dirty',
                                                                     'financial_dirty', ])
            if len(self.log_entries) > 0:
                # insert log entry
                LogClientEntry.objects.tenant_db_for(self.client_id).bulk_create(self.log_entries, ignore_conflicts=True)
            #
            self.sale_item = []
            self.log_entries = []

        print(f"------ End execute reset Drop Fee for Is Prime Sale --------")
