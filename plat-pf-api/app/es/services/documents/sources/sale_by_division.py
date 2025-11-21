from abc import ABC
from app.es.variables.template import SALE_BY_DIVISION_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class SaleByDivisionDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_BY_DIVISION_INDEX_TEMPLATE
