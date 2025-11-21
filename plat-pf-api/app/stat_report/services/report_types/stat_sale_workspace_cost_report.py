import logging, copy
from datetime import datetime

from django.utils import timezone
from typing import List
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Count, Q
from app.financial.models import SaleItem
from app.stat_report.models import ClientReportCost
from app.stat_report.services.report_types.stat_report import StatReporter

logger = logging.getLogger(__name__)


class StatSaleClientCostReport(StatReporter):

    def validate(self):
        pass

    def process(self):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}][process] Begin ...")

    @classmethod
    def calculate_client_report_cost(cls, client_ids: List[str], from_date: datetime.date, to_date: datetime.date):
        assert len(client_ids) > 0, f"Client IDs is not empty"
        objs_create = []
        objs_update = []
        for client_id in client_ids:
            logger.info(f"[{cls.__class__.__name__}][{client_id}] progress ...")
            results: dict = SaleItem.objects.tenant_db_for(client_id).aggregate(
                total_sales=Count('pk', filter=Q(sale_date__date__lte=to_date)),
                total_30d_sales=Count('pk', filter=Q(sale_date__date__gte=from_date, sale_date__date__lte=to_date))
            )
            logger.info(f"[{cls.__class__.__name__}][{client_id}] results = {results}")
            date_request = copy.deepcopy(to_date)
            date_request = date_request.replace(day=1)
            try:
                obj = ClientReportCost.objects.tenant_db_for(DEFAULT_DB_ALIAS).get(client_id=client_id,
                                                                                   date=date_request)
                for k, v in results.items():
                    setattr(obj, k, v)
                obj.modified = timezone.now()
                objs_update.append(obj)
            except Exception as ex:
                logger.info(f"[{cls.__class__.__name__}][{client_id}] {ex}")
                objs_create.append(ClientReportCost(client_id=client_id, date=date_request, **results))

        ClientReportCost.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_create(objs_create, ignore_conflicts=True)
        ClientReportCost.objects.tenant_db_for(DEFAULT_DB_ALIAS).bulk_update(objs_update,
                                                                             fields=['total_sales', 'total_30d_sales',
                                                                                     'modified'])

    def complete(self):
        logger.info(f"[{self.__class__.__name__}][{self.client_id}][complete] Begin ...")
