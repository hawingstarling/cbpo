from abc import ABC
from app.es.variables.template import SALE_BY_DOLLAR_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class SaleByDollarDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_BY_DOLLAR_INDEX_TEMPLATE
