from abc import ABC
from app.es.variables.template import TSTYLE_MTD_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class TopASINsMTDDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = TSTYLE_MTD_INDEX_TEMPLATE
