import logging

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.db import connection, transaction

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class LargeTablePagination(Paginator):

    @cached_property
    def count(self):
        try:
            with transaction.atomic(), connection.cursor() as cursor:
                self.set_local_statement_timeout(cursor, 200)
                try:
                    return super().count
                except Exception as ex:
                    self.set_local_statement_timeout(cursor, 0)
                    raise ex
                finally:
                    self.set_local_statement_timeout(cursor, 0)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][count] {ex}")
            return self.estimate_count

    def set_local_statement_timeout(self, cursor, timeout: int = 0):
        logger.info(
            f"[{self.__class__.__name__}][set_local_statement_timeout] SET LOCAL statement_timeout TO {timeout} running ...")
        cursor.execute(f'SET LOCAL statement_timeout TO {timeout};')

    @cached_property
    def estimate_count(self):
        query = self.object_list.query
        if not query.where:
            try:
                logger.info(
                    f"[{self.__class__.__name__}][estimate_count] SELECT reltuples FROM pg_class WHERE relname = {[query.model._meta.db_table]}")
                # count estimate
                with transaction.atomic(), connection.cursor() as cursor:
                    cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s", [query.model._meta.db_table])
                    count = int(cursor.fetchone()[0])
            except Exception as ex:
                logger.error(f"[{self.__class__.__name__}][estimate_count] {ex}")
                count = self.alt_count
        else:
            count = self.alt_count
        return count

    @cached_property
    def alt_count(self):
        try:
            # count index
            with transaction.atomic(), connection.cursor() as cursor:
                query_plan = self.object_list.explain()
                logger.info(f"[{self.__class__.__name__}][alt_count] {query_plan}")
                count = int(str(query_plan).split("width=")[0].split("rows=")[1].strip())
                return count
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][alt_count] {ex}")
            return 9999999999
