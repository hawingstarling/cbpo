from abc import ABC
from app.es.variables.template import BRAND_30_DAY_SALE_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class Brand30DaySaleDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = BRAND_30_DAY_SALE_INDEX_TEMPLATE
