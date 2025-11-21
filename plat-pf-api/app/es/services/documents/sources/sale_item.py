from abc import ABC
from app.es.variables.template import SALE_ITEM_INDEX_TEMPLATE
from .base import DataSourceDocumentBase

class SaleItemDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_ITEM_INDEX_TEMPLATE