from abc import ABC
from app.es.variables.template import OVERALL_SALES_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class OverallSalesDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = OVERALL_SALES_INDEX_TEMPLATE
