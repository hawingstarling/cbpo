import maya
from django.core.management.base import BaseCommand

from app.core.utils import hashlib_content
from app.financial.models import ClientPortal, Channel, SaleItem
from app.financial.services.utils.common import chunks_size_list
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY, MODE_RUN_IMMEDIATELY


class Command(BaseCommand):
    help = "Command sync schema sale item table to table flatten."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for make data source calculate')

        parser.add_argument('-fd', '--from_date', type=str,
                            help='Provide start date for sync live feed. Format YYYY-MM-DD')

        parser.add_argument('-td', '--to_date', type=str,
                            help='Provide end date for sync live feed. Format YYYY-MM-DD')

    def handle(self, *args, **options):
        print("---- Begin sync sale item to table flatten ----")
        client_id = options['client_id']
        #
        from_date = options['from_date']
        to_date = options['to_date']
        #
        if not client_id or not from_date or not to_date:
            print('Pls input client id, jwt_token, from_date, to_date for generate ds financial')
            return

        try:
            ClientPortal.objects.tenant_db_for(client_id).get(id=client_id)
        except ClientPortal.DoesNotExist:
            print('Client Portal not exist in system')
            return
        #
        try:
            maya.parse(f"{from_date} 00:00:00").datetime()
            maya.parse(f"{to_date} 23:59:59").datetime()
            # update financial dirty 
            channels = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True)
            for channel in channels:
                marketplace = channel.name
                print(f'------ Begin update financial dirty for ws : {client_id} , channel : {marketplace} --------')

                queryset = SaleItem.objects.tenant_db_for(client_id).filter(client_id=client_id, sale__channel=channel,
                                                                            sale_date__date__gte=from_date,
                                                                            sale_date__date__lte=to_date)
                #
                print(f"------ query set : {queryset.query} ------")
                #
                sale_item_ids = list(queryset.values_list('id', flat=True))
                chunks = chunks_size_list(sale_item_ids, 1000)
                for chunk in chunks:
                    print(f"------ process sale item ids : {chunk} ------")
                    meta = dict(client_id=client_id, marketplace=marketplace, sale_item_ids=chunk)
                    hash_content = hashlib_content(meta)
                    data = dict(
                        name=f"split_sale_item_financial_ws_{marketplace}_{hash_content}",
                        job_name="app.financial.jobs.sale_financial.handler_trigger_split_sale_item_financial_ws",
                        module="app.financial.jobs.sale_financial",
                        method="handler_trigger_split_sale_item_financial_ws",
                        meta=meta
                    )
                    register(category=SYNC_DATA_SOURCE_CATEGORY, client_id=client_id, **data,
                             mode_run=MODE_RUN_IMMEDIATELY)

        except Exception as ex:
            print(f'------ Error make datasource to ds : {ex}')
            return
        print(f'------ Generate DS Financial View Success --------')
