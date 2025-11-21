from abc import ABC
from app.es.variables.template import FF_MONTHLY_SALE_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class FFMonthlySaleDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = FF_MONTHLY_SALE_INDEX_TEMPLATE
