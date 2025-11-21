from abc import ABC
from app.es.variables.template import YOY_30_DAY_SALE_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class YOY30DaySaleDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = YOY_30_DAY_SALE_INDEX_TEMPLATE
