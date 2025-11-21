from django.core.management.base import BaseCommand
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils import timezone

from app.financial.models import ClientPortal, DataFlattenTrack
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.services.schema_datasource import SyncSchemaDatasource
from app.financial.services.utils.common import get_id_data_source_3rd_party, get_flatten_source_name
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE_ANALYSIS_LIST, FLATTEN_PG_SOURCE, \
    FLATTEN_ES_SOURCE
from app.financial.variable.job_status import SUCCESS
from app.financial.services.utils.source_config import data_source_generator_config


class Command(BaseCommand):
    help = "Command sync schema sale item table to table flatten."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for sync sale items data to table flatten')
        parser.add_argument('-ds', '--register_ds', action='store_true',
                            help='Create external_id to datasource service')
        parser.add_argument('-jwt', '--jwt_token', type=str, help='Provide access token for call DS service make ds')
        parser.add_argument('-new', '--is_new_source', action='store_true', help='Enable/Disable make new source')
        parser.add_argument('-type', '--flatten_type', type=str, help='Flatten type sync')
        parser.add_argument('-source', '--source', type=str, help='Flatten source on demand')
        parser.add_argument('-size', '--bulk_size', type=int, help='Bulk size sync data')
        parser.add_argument('-sync_conf', '--sync_schema_config', action='store_true',
                            help='Sync mapping elastic search')

    def get_or_create_data_source(self, jwt_token, client_id, type_flatten, source):
        flatten_name = get_flatten_source_name(client_id, type_flatten)
        data_source = DataSource(client_id=client_id, type_flatten=type_flatten,
                                 table=flatten_name, access_token=jwt_token,
                                 api_centre=ApiCentreContainer.data_source_central(), source=source)
        external_id = get_id_data_source_3rd_party(source, client_id, type_flatten)

        doc = data_source.get_or_create_data_source(external_id)
        return doc

    def register_ds(self, jwt_token, client_id, type_flatten, config):
        #
        print(f"---- register_ds :{client_id} ----")
        try:
            data_flatten_track, _ = DataFlattenTrack.objects.tenant_db_for(client_id).get_or_create(
                client_id=client_id, type=type_flatten)
            # PG
            if data_flatten_track.data_source_id is None:
                pg_doc = self.get_or_create_data_source(jwt_token, client_id, type_flatten, FLATTEN_PG_SOURCE)
                data_flatten_track.data_source_id = pg_doc.get('external_id', None)
                print(f"pg_external_id  = {data_flatten_track.data_source_id}")
            # ES
            if data_flatten_track.data_source_es_id is None:
                es_doc = self.get_or_create_data_source(jwt_token, client_id, type_flatten, FLATTEN_ES_SOURCE)
                data_flatten_track.data_source_es_id = es_doc.get('external_id', None)
                print(f"es_external_id = {data_flatten_track.data_source_es_id}")

            data_flatten_track.status = SUCCESS
            data_flatten_track.live_feed = True
            data_flatten_track.modified = timezone.now()
            data_flatten_track.save()
            return True
        except Exception as ex:
            print(f"[sync_data_source_id][{client_id}][type_flatten] {ex}")
        return False

    def handle(self, *args, **options):
        print("---- Begin sync sale item to table flatten ----")
        client_id = options['client_id']
        is_new_source = options['is_new_source']
        register_ds = options['register_ds']
        jwt_token = options['jwt_token']
        flatten_type = options['flatten_type']
        source = options['source']
        sync_schema_config = options['sync_schema_config']
        clients = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
        if client_id:
            clients = clients.filter(pk=client_id)
        if clients.count() == 0:
            print(
                "Client Id is incorrect or haven't been synced to PF. Please sync workspace from portal before syncing the data source")
            return
        if flatten_type:
            flatten_types = [flatten_type]
        else:
            flatten_types = DATA_FLATTEN_TYPE_ANALYSIS_LIST
        stat = {'total': clients.count(), 'success': 0, 'error': 0}
        for client in clients.iterator():
            #
            success = True
            sync_schema_ds = SyncSchemaDatasource(client_id=client.id, is_new_source=is_new_source,
                                                  source=source,
                                                  bulk_size=options.get('bulk_size', 1000),
                                                  sync_schema_config=sync_schema_config)
            for flatten_type in flatten_types:
                print(f"---- Workspace Id :{client.id} ----")
                print(f"---- Flatten type : {flatten_type} -----")
                config = data_source_generator_config()[flatten_type]
                # register_ds
                if register_ds:
                    result = self.register_ds(jwt_token, client_id, flatten_type, config)
                    if not result:
                        success = success & False
                        continue
                #
                try:
                    sync_schema_ds.process_flatten(flatten_type, config)
                    success = success & True
                except Exception as ex:
                    success = success & False
                    print("---- sync sale items to datasource error {}".format(ex))
            if success:
                stat['success'] += 1
            else:
                stat['error'] += 1
        print(stat)
        print("---- End sync sale item to table flatten ----")
