from itertools import islice
import os
import logging
from django.conf import settings
from decimal import Decimal

from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_SOURCES_ES_DEFAULT, \
    FLATTEN_ES_SOURCE, FLATTEN_PG_SOURCE

next_cent = settings.PLAT_IMPORT_CURRENCY_NEXT_CENT if hasattr(
    settings, 'PLAT_IMPORT_CURRENCY_NEXT_CENT') else 0

logger = logging.getLogger(__name__)


def is_the_same_currency(a: any, b: any, column: str = None):
    try:
        if column in ['cog', 'unit_cog']:
            float(a)
            float(b)
            return Decimal(format(a, '.2f')) == Decimal(format(b, '.2f'))
        else:
            return a == b
    except BaseException as err:
        logger.debug(f"[is_the_same][{a}][{b}][{column}] {err}")
        return a == b


def round_currency(value):
    _round = round(value, 2)
    _temp = _round - value
    if _temp >= 0:
        value = _round
    else:
        value = round(_round + next_cent, 2)
    return value


def delete_file_local(file_path):
    if os.path.exists(file_path) is True:
        os.remove(file_path)


def chunks_size_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def chunks_size_dict(dict, n):
    """Yield successive n-sized chunks from dict."""
    it = iter(dict)
    for i in range(0, len(dict), n):
        yield {k: dict[k] for k in islice(it, n)}


def get_flatten_source_name(client_id: str, type_flatten: str = FLATTEN_SALE_ITEM_KEY) -> str:
    return f"flatten_{str.lower(type_flatten)}_{client_id.replace('-', '_')}"


def get_id_data_source_3rd_party(source: str, client_id: str, type_flatten: str = FLATTEN_SALE_ITEM_KEY, prefix: str = 'pf') -> str:
    return f"{prefix.lower()}:{source.lower()}:{client_id}:{str.lower(type_flatten)}"


def get_source_default(type_flatten: str = FLATTEN_SALE_ITEM_KEY) -> str:
    return FLATTEN_ES_SOURCE if type_flatten in FLATTEN_SOURCES_ES_DEFAULT else FLATTEN_PG_SOURCE
