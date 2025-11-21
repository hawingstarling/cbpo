from abc import ABC
from app.es.variables.template import TSTYLE_YTD_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class TopASINsYTDDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = TSTYLE_YTD_INDEX_TEMPLATE
