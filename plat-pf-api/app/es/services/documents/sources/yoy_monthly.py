from abc import ABC
from app.es.variables.template import YOY_MONTHLY_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class YOYMonthlyDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = YOY_MONTHLY_INDEX_TEMPLATE
