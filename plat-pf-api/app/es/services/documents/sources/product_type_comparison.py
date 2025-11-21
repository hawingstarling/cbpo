from abc import ABC
from app.es.variables.template import PRODUCT_TYPE_COMPARISON_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class ProductTypeComparisonDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = PRODUCT_TYPE_COMPARISON_INDEX_TEMPLATE
