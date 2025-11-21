from abc import ABC
from app.es.variables.template import BROKEN_DOWN_SALE_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class BrokenDownSaleDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = BROKEN_DOWN_SALE_INDEX_TEMPLATE
