from abc import ABC
from app.es.variables.template import ADVERTISING_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class AdvertisingDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = ADVERTISING_INDEX_TEMPLATE
