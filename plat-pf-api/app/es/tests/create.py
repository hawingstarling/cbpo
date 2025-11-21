import logging

from app.database.variable.schema_tables.financial import DB_TABLE_SALE_ITEM_TEMPLATE
from app.es.helper import get_es_sources_configs

logger = logging.getLogger(__name__)


def create_index_document(client_id, source_type):
    source_service = get_es_sources_configs()[source_type](client_id)
    exist_index = source_service.exist_index
    logger.info(f"[{source_service.index}] exist index {exist_index}")
    if not exist_index:
        source_service.create_index()
    #
    sql = f"""
        
        SELECT * FROM {DB_TABLE_SALE_ITEM_TEMPLATE.format(client_id_tbl=client_id.replace('-', '_'))} 
        ORDER BY created DESC limit 3
    
    """
    source_service.on_validate()
    source_service.on_process(data=sql, action="delete", key_id="id")
    source_service.on_complete()
