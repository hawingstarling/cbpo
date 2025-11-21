import logging, copy
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from app.financial.models import DataFlattenTrack, ClientPortal
from app.financial.services.data_flatten import DataFlatten
from app.financial.services.flattens_settings.generate import GenerateClientSource
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE_CALCULATE_LIST, FLATTEN_ES_SOURCE
from django.utils import timezone
from app.financial.services.utils.source_config import data_source_generator_config
from app.financial.variable.job_status import SUCCESS, ERROR
from app.job.utils.helper import register_list
from app.job.utils.variable import DATA_SOURCE_CALCULATION_CATEGORY, MODE_RUN_IMMEDIATELY
from config.settings.common import DS_TOKEN

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Command sync schema sale item table to table flatten."

    def add_arguments(self, parser):
        parser.add_argument('-c', '--client_id', type=str,
                            help='Provide client id for make data source calculate')
        parser.add_argument('-ds', '--register_ds', action='store_true',
                            help='Create external_id to datasource service')
        parser.add_argument('-ds_type', '--datasource_type', type=str,
                            help='Provide data source type for generate ds')
        parser.add_argument('-new_tb', '--new_table', action='store_true', help='ON/OFF create new table schema')
        parser.add_argument('-use_queue', '--use_queue', action='store_true', help='ON/OFF create new table schema')

    def handle(self, *args, **options):
        print("---- Begin sync sale item to table flatten ----")
        client_id_request = options['client_id']
        ds_type = options['datasource_type']
        new_table = options['new_table']
        use_queue = options['use_queue']
        #
        qs = ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
        if client_id_request:
            qs = qs.filter(pk=client_id_request)

        client_ids = qs.values_list("pk", flat=True)

        if ds_type:
            ds_type_config = [ds_type]
        else:
            ds_type_config = copy.deepcopy(DATA_FLATTEN_TYPE_CALCULATE_LIST)

        # exclude ds flatten data live feed
        stats = {}
        print(ds_type_config)
        for client_id in client_ids:
            client_id = str(client_id)
            stats.update({
                client_id: {'total': len(ds_type_config), 'success': 0, 'error': 0, 'errors_detail': []},
            })
            jobs = []
            time_now = timezone.now()
            for type_flatten in ds_type_config:

                config = data_source_generator_config().get(type_flatten, None)

                if not config:
                    stats[client_id]['error'] += 1
                    logger.error(f"[Tasks][flat_ds_calculate] type flatten {type_flatten} invalid")
                    continue

                data_flatten_track, _ = (DataFlattenTrack.objects.tenant_db_for(client_id)
                                         .get_or_create(client_id=client_id, type=type_flatten))
                data_flatten_service = DataFlatten(
                    client_id=client_id,
                    type_flatten=type_flatten,
                    **config,
                    source=data_flatten_track.source,
                    batch_size=data_flatten_track.batch_size,
                    last_run_synced=data_flatten_track.last_run,
                    last_rows_synced=data_flatten_track.last_rows_synced
                )
                try:

                    if not data_flatten_track.data_source_id or not data_flatten_track.data_source_es_id:
                        flattens_settings_generate = GenerateClientSource(client_id=client_id, access_token=DS_TOKEN,
                                                                          token_type="DS_TOKEN")
                        if not data_flatten_track.data_source_id:
                            data_flatten_track.data_source_id = flattens_settings_generate.generate_data_source(
                                type_flatten=type_flatten)
                        if not data_flatten_track.data_source_es_id:
                            data_flatten_track.data_source_es_id = flattens_settings_generate.generate_data_source(
                                type_flatten=type_flatten, source=FLATTEN_ES_SOURCE)

                    data_flatten_track.status = SUCCESS
                    data_flatten_track.live_feed = True
                    data_flatten_track.modified = time_now
                    data_flatten_track.save()
                    # Drop table if request new table
                    if new_table and data_flatten_service.source_exist:
                        data_flatten_service.drop_flatten_exists()
                    #
                    if not use_queue:
                        data_flatten_service.do_flatten()
                        data_flatten_track.last_run = time_now
                        data_flatten_track.last_rows_synced = data_flatten_service.total_rows_synced
                        data_flatten_track.save()
                    else:
                        job = dict(
                            client_id=client_id,
                            name=f"generate_ds_calculate_{type_flatten}",
                            job_name="app.financial.jobs.data_flatten.flat_ds_calculate",
                            module="app.financial.jobs.data_flatten",
                            method="flat_ds_calculate",
                            meta=dict(client_id=client_id, type_flatten=type_flatten)
                        )
                        jobs.append(job)
                    stats[client_id]['success'] += 1
                except Exception as ex:
                    data_flatten_track.status = ERROR
                    data_flatten_track.log = str(ex)
                    data_flatten_track.save(update_fields=["status", "log"])
                    print(f'------ Error make datasource to ds : {ex}')
                    stats[client_id]['error'] += 1
                    stats[client_id]['errors_detail'] += [{'type_flatten': type_flatten, 'error': str(ex)}]
            if len(jobs) > 0 and use_queue:
                logger.info(f"[generate_ds_calculate][{client_id}] total jobs = {len(jobs)}")
                register_list(DATA_SOURCE_CALCULATION_CATEGORY, jobs, mode_run=MODE_RUN_IMMEDIATELY)
        print(stats)
        print("---- End sync sale item to table flatten ----")
