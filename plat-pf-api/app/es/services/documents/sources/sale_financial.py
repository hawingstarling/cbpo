from abc import ABC
from app.es.variables.template import SALE_FINANCIAL_INDEX_TEMPLATE
from .base import DataSourceDocumentBase

class SaleFinancialDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_FINANCIAL_INDEX_TEMPLATE