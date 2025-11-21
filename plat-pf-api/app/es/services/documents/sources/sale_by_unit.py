from abc import ABC
from app.es.variables.template import SALE_BY_UNIT_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class SaleByUnitDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_BY_UNIT_INDEX_TEMPLATE
