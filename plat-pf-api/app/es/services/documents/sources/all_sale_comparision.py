from abc import ABC
from app.es.variables.template import ALL_SALE_COMPARISION_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class AllSaleComparisionDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = ALL_SALE_COMPARISION_INDEX_TEMPLATE
