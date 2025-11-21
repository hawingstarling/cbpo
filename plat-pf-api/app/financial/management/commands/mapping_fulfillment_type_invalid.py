import maya
from auditlog.models import LogEntry
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from app.financial.jobs.data_flatten import flat_sale_items_bulks_sync_task
from app.financial.models import SaleItem, FulfillmentChannel, Channel, LogClientEntry
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.database.helper import get_connection_workspace
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_SALE_ITEM_FINANCIAL_KEY

FF_TYPE_INVALID = ['DS', 'Prime', 'RA', 'Rapid Access', 'Store Prime']


class Command(BaseCommand):
    help = "Command migrate fulfillment correct and clean fulfillment type invalid."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for make data source calculate')

        parser.add_argument('-mk', '--marketplace', type=str,
                            help='Provide marketplace amazon.com, amazon.ca, amazon.com.mx ...')

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-rm_ff_invalid', '--remove_ff_invalid', action='store_true',
                            help='Enable/Disable delete ff invalid')

    def get_config_mapping(self, client_id):
        return {
            'DS': FulfillmentChannel.objects.tenant_db_for(client_id).get(name='MFN-DS'),
            'Prime': FulfillmentChannel.objects.tenant_db_for(client_id).get(name='MFN-Prime'),
            'RA': FulfillmentChannel.objects.tenant_db_for(client_id).get(name='MFN-RA'),
            'Rapid Access': FulfillmentChannel.objects.tenant_db_for(client_id).get(name='MFN-RA'),
            'Store Prime': FulfillmentChannel.objects.tenant_db_for(client_id).get(name='MFN-Prime')
        }

    @transaction.atomic()
    def handle(self, *args, **options):
        print("---- Begin mapping fulfillment type invalid ----")
        print(f"Fulfillment Type name invalid config : {FF_TYPE_INVALID}")

        client_id = options['client_id']
        #
        if not client_id:
            print('Pls input client_id for reset mapping')
            return

        marketplace = options['marketplace']

        if marketplace:
            marketplaces = [marketplace]
        else:
            marketplaces = list(
                Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True))

        ff_type_mapping = self.get_config_mapping(client_id)

        queryset = SaleItem.objects.tenant_db_for(client_id).filter(client_id=client_id,
                                                                    sale__channel__name__in=marketplaces) \
            .order_by('created')

        #
        fd = options['from_date']
        td = options['to_date']

        if fd and td:
            fd = maya.parse(fd).datetime().date()
            td = maya.parse(td).datetime().date()
            queryset = queryset.filter(sale_date__gte=fd, sale_date__lte=td)

        queryset_ff_invalid = queryset.filter(fulfillment_type__name__in=FF_TYPE_INVALID)

        print(f"queryset: {queryset_ff_invalid.query}")

        print(f"total items invalid: {queryset_ff_invalid.count()}")

        queryset_ids = queryset.filter(pk__in=list(queryset_ff_invalid.values_list('pk', flat=True)))

        p = Paginator(queryset_ids, 1000)

        num_pages = p.num_pages

        for page in range(num_pages):

            log_entries = []
            sale_items = []

            #
            page_current = page + 1

            objs = p.page(number=page_current).object_list

            print(f"processing page {page_current} , total = {len(objs)} ...")

            for obj in objs:
                val = ff_type_mapping[obj.fulfillment_type.name]
                changes = {'fulfillment_type': [obj.fulfillment_type.name, val.name]}
                obj.fulfillment_type = ff_type_mapping[obj.fulfillment_type.name]
                obj.modified = timezone.now()
                obj.dirty = True
                obj.financial_dirty = True
                sale_items.append(obj)
                #
                log_entry = AuditLogCoreManager(client_id=client_id).set_actor_name('') \
                    .create_log_entry_from_compared_changes(obj, changes, action=LogEntry.Action.UPDATE)
                log_entries.append(log_entry)

            SaleItem.objects.tenant_db_for(client_id).bulk_update(sale_items,
                                                                  fields=['fulfillment_type', 'dirty',
                                                                          'financial_dirty', 'modified'])
            client_db = get_connection_workspace(client_id)
            LogClientEntry.objects.tenant_db_for(client_id).bulk_create(log_entries, ignore_conflicts=True)
            #
            # sync to flatten
            if queryset.filter(dirty=True).count() > 0:
                flat_sale_items_bulks_sync_task(client_id=client_id, type_flatten=FLATTEN_SALE_ITEM_KEY)
            if queryset.filter(financial_dirty=True).count() > 0:
                flat_sale_items_bulks_sync_task(client_id=client_id, type_flatten=FLATTEN_SALE_ITEM_FINANCIAL_KEY)

        remove_ff_invalid = options['remove_ff_invalid']
        if remove_ff_invalid:
            print(f"delete fulfillment type invalid : {FF_TYPE_INVALID} ...")
            FulfillmentChannel.objects.tenant_db_for(client_id).filter(name__in=FF_TYPE_INVALID).delete()

        print(f'------ End mapping fulfillment type invalid --------')
