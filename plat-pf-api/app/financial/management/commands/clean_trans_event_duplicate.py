from django.core.management.base import BaseCommand
from app.financial.models import GenericTransaction, Channel
from django.db.models import Count
from django.db import connections, DatabaseError
from app.financial.jobs.event import handler_trigger_trans_event_sale_item_ws
from app.database.helper import get_connection_workspace


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str, help='Provide client_id for clean trans financial event duplicate')

    def handle(self, *args, **options):
        
        client_id = options['client_id']

        if client_id  is None:
            print("Please input client_id (-c --client_id). Run python manage.py clean_trans_event_duplicate --help")
            return

        channels = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True)

        for channel in channels:

            channel_id = str(channel.pk)

            # get all channel sale id have trans event type Adjustment duplicate
            channel_sale_ids = GenericTransaction.objects.tenant_db_for(client_id).filter(
                client_id=client_id, 
                channel_id=channel_id, 
                event='adjustment',
                sku__isnull=True,
                category__isnull=True,
            ).values('channel_sale_id', 'type', 'event').annotate(total=Count('type')) \
                .filter(total__gt=1) \
                .values_list('channel_sale_id', flat=True).distinct()

            print(f"[{client_id}][{channel.name}]: query get channel sale ids duplicate trans : {channel_sale_ids.query}")

            if len(channel_sale_ids) == 0:
                print(f'------ Not found channel sale ids duplicate channel ws : {client_id}, channel : {channel.name} ------')
                continue

            print(f"------ Begin clean data trans event duplicate channel ws : {client_id}, channel : {channel.name} ------")

            # build sql clean channel sale ids duplicate & cache channel sale ids

            sql = f"""
                WITH trans_event_duplicate AS (
                    (
                        SELECT DISTINCT channel_sale_id 
                        FROM financial_generictransaction 
                        WHERE  
                            is_removed = False 
                            AND category IS NULL 
                            AND sku IS NULL 
                            AND channel_id = '{channel_id}' 
                            AND client_id = '{client_id}' 
                            AND event = 'adjustment' 
                        GROUP BY channel_sale_id, type, event 
                        HAVING COUNT(type) > 1
                    )
                )

                DELETE FROM 
                    financial_generictransaction 
                WHERE 
                    is_removed = False 
                    AND client_id = '{client_id}' AND channel_id = '{channel_id}' 
                    AND event = 'adjustment' AND sku IS NULL
                    AND channel_sale_id IN (SELECT trans_event_duplicate.channel_sale_id FROM trans_event_duplicate);
                
                TRUNCATE financial_cachetransaction;
            """

            print(sql)

            client_db = get_connection_workspace(client_id)

            with connections[client_db].cursor() as cursor:
                try:
                    cursor.execute(sql)

                except Exception or DatabaseError as err:
                    print(err)
                    cursor.execute("ROLLBACK")
                    return

            # trigger sync financial for channel_sale ids
            # per chunk size 200 records channel sale ids
            chunk_channel_sale_ids = utils.chunks_size_list(channel_sale_ids, 200)

            for chunk in chunk_channel_sale_ids:
                print(f"Sync for channel sale ids : {chunk}")
                handler_trigger_trans_event_sale_item_ws.delay(client_id=client_id, marketplace=channel.name, amazon_order_ids=chunk)
