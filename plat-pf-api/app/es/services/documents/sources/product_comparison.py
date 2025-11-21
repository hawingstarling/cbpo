from abc import ABC
from app.es.variables.template import PRODUCT_COMPARISON_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class ProductComparisonDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = PRODUCT_COMPARISON_INDEX_TEMPLATE
