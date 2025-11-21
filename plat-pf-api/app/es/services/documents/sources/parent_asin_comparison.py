from abc import ABC
from app.es.variables.template import PARENT_ASIN_COMPARISON_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class ParentAsinComparisonDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = PARENT_ASIN_COMPARISON_INDEX_TEMPLATE
