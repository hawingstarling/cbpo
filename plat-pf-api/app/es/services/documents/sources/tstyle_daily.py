from abc import ABC
from app.es.variables.template import TSTYLE_DAILY_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class TopASINsDailyDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = TSTYLE_DAILY_INDEX_TEMPLATE
