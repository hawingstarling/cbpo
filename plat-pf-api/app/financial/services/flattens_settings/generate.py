import logging
from app.core.utils import check_current_is_test_env
from app.financial.jobs.data_flatten import flat_sale_items
from app.financial.models import DataFlattenTrack
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.services.schema_datasource import SyncSchemaDatasource
from app.financial.services.utils.common import get_flatten_source_name, get_id_data_source_3rd_party
from app.financial.services.utils.source_config import data_source_generator_config
from app.financial.variable.data_flatten_variable import DATA_FLATTEN_TYPE_LIST, FLATTEN_PG_SOURCE, FLATTEN_ES_SOURCE, \
    DATA_FLATTEN_TYPE_ANALYSIS_LIST, FLATTEN_SOURCES_ES_DEFAULT
from app.financial.variable.job_status import ERROR, SUCCESS
from app.job.utils.helper import register_list
from app.job.utils.variable import COMMUNITY_CATEGORY

logger = logging.getLogger(__name__)


class GenerateClientSource:
    def __init__(self, client_id: str, access_token: str = None, token_type: str = 'JWT', **kwargs):
        self.client_id = client_id
        self.access_token = access_token
        self.token_type = token_type
        self.sync_schema_ds = SyncSchemaDatasource(client_id=client_id)
        self.kwargs = kwargs

    @property
    def force_run(self):
        return self.kwargs.get('force_run', False)

    def generate_data_source(self, type_flatten, source=FLATTEN_PG_SOURCE):
        #
        flatten_source_name = get_flatten_source_name(self.client_id, type_flatten)
        data_source = DataSource(client_id=self.client_id, type_flatten=type_flatten,
                                 table=flatten_source_name, access_token=self.access_token,
                                 api_centre=ApiCentreContainer.data_source_central(), source=source,
                                 token_type=self.token_type)
        #
        external_id = get_id_data_source_3rd_party(source=source, client_id=self.client_id, type_flatten=type_flatten)
        doc = data_source.get_or_create_data_source(external_id)
        return doc.get('external_id', None)

    @property
    def data_flattens_type_list(self):
        if self.kwargs.get('flatten_type'):
            return [self.kwargs['flatten_type']]
        else:
            return DATA_FLATTEN_TYPE_LIST

    def process(self):
        ds_jobs_data = []

        for type_flatten in self.data_flattens_type_list:

            logger.info(f"[{self.__class__.__name__}] begin generate flatten type = {type_flatten}")

            data_flatten_track, _ = DataFlattenTrack.objects.tenant_db_for(self.client_id).get_or_create(
                client_id=self.client_id, type=type_flatten)
            #
            if not data_flatten_track.data_source_id or not data_flatten_track.data_source_es_id \
                    or data_flatten_track.status == ERROR:
                data_source_id = self.generate_data_source(type_flatten)
                data_source_es_id = self.generate_data_source(type_flatten, source=FLATTEN_ES_SOURCE)
                # PG
                data_flatten_track.data_source_id = data_source_id
                # ES
                data_flatten_track.data_source_es_id = data_source_es_id
                # Source default to ES
                is_test_env = check_current_is_test_env()
                if type_flatten in FLATTEN_SOURCES_ES_DEFAULT and not is_test_env:
                    data_flatten_track.source = FLATTEN_ES_SOURCE
                data_flatten_track.save()

                # Generate ds
                if type_flatten in DATA_FLATTEN_TYPE_ANALYSIS_LIST:
                    config = data_source_generator_config()[type_flatten]
                    self.sync_schema_ds.process_flatten(type_flatten, config)
                    data_flatten_track.status = SUCCESS
                    data_flatten_track.live_feed = True
                    data_flatten_track.save()
                else:
                    if not self.force_run:
                        #
                        ds_jobs_data.append(
                            dict(
                                client_id=self.client_id,
                                name=f"generating_datasource_{type_flatten}",
                                job_name="app.financial.jobs.data_flatten.flat_sale_items",
                                module="app.financial.jobs.data_flatten",
                                method="flat_sale_items",
                                meta=dict(client_id=self.client_id, type_flatten=type_flatten)
                            )
                        )
                    else:
                        flat_sale_items(client_id=self.client_id, type_flatten=type_flatten)
        if len(ds_jobs_data) > 0:
            register_list(COMMUNITY_CATEGORY, ds_jobs_data)
