from abc import ABC
from app.es.variables.template import TSTYLE_30_DAYS_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class TopASINs30DaysDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = TSTYLE_30_DAYS_INDEX_TEMPLATE
