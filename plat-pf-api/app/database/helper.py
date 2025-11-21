import logging
from django.conf import settings
from django.db.utils import DEFAULT_DB_ALIAS

logger = logging.getLogger(__name__)


def get_connection_workspace(client_id: str):
    try:
        from app.database.models import DatabaseClientConfig
        db_name = DatabaseClientConfig.objects.get(client_id=client_id).database.name
    except Exception as ex:
        # logger.error(f"[{client_id}][get_connection_workspace] {ex}")
        db_name = DEFAULT_DB_ALIAS
    return db_name


def get_db_client_config(client_id):
    from .models import DatabaseClientConfig
    try:
        es_client = DatabaseClientConfig.objects.get(client_id=client_id)
    except DatabaseClientConfig.DoesNotExist:
        # logger.error(f"[get_db_client_config][{client_id}] using config default")
        es_client = None
    return es_client


def get_db_url_client(client_id):
    try:
        db_url = get_db_client_config(client_id).database.url
    except Exception as ex:
        logger.debug(f"[get_db_url_client][{client_id}] {ex}")
        db_url = settings.DATABASE_URL
    return db_url
