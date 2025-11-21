from abc import ABC
from app.es.variables.template import PRODUCT_SALE_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class ProductSaleDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = PRODUCT_SALE_INDEX_TEMPLATE
