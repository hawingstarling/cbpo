from abc import ABC
from app.es.variables.template import SALE_BIG_MOVES_INDEX_TEMPLATE
from .base import DataSourceDocumentBase


class SaleBigMovesDocument(DataSourceDocumentBase, ABC):
    INDEX_TEMPLATE = SALE_BIG_MOVES_INDEX_TEMPLATE
