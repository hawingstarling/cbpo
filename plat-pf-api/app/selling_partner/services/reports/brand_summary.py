import copy
import logging
from datetime import datetime
from typing import List, Union
import pytz
from django.db.models import Q, QuerySet
from xlsxwriter import Workbook
from app.financial.models import SaleItem
from app.financial.services.exports.schema import EXCEL, EXCEL_XLSX
from app.financial.variable.sale_status_static_variable import SALE_SHIPPED_STATUS, SALE_UNSHIPPED_STATUS, \
    SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS, SALE_CANCELLED_STATUS, RETURN_REVERSED_STATUS
from app.selling_partner.models import SPReportClient
from app.selling_partner.services.reports.as_sqls.brand_summary import SQL_PLAINTEXT
from app.selling_partner.services.reports.base import SPClientReportAggregateBase
from app.selling_partner.variables.report_status import READY_STATUS, ERROR_STATUS

logger = logging.getLogger(__name__)

SHIPPED_SHEET = "Shipped"
REFUND_SHEET = "Refunded"
CANCELLED_SHEET = "Cancelled"
RETURN_REVERSED_SHEET = "Return"


class SPClientBrandAggregateReport(SPClientReportAggregateBase):
    __FILE_NAME_TEMPLATE__ = "Brands-Summary-Data-Report"
    __SHEETS_CONFIG__ = {
        SHIPPED_SHEET: [SALE_SHIPPED_STATUS, SALE_UNSHIPPED_STATUS],
        REFUND_SHEET: [SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS],
        CANCELLED_SHEET: [SALE_CANCELLED_STATUS],
        RETURN_REVERSED_SHEET: [RETURN_REVERSED_STATUS],
    }
    __FILE_TYPE__ = EXCEL
    __FILE_EXTENSION__ = EXCEL_XLSX
    __WRITER_ENGINE__ = "openpyxl"
    __DF_MODE__ = "a"
    __APPEND_HEADER_FILE__ = False
    __FILE_READ_SQL__ = True

    def __init__(self, client_id: str, object_id: str, *args, **kwargs):
        super().__init__(client_id, object_id, *args, **kwargs)
        self.date_range = self._get_date_range()
        self.client_id_db = str(self._client_id).replace("-", "_")

    @property
    def file_name_report(self):
        return f"{self.__FILE_NAME_TEMPLATE__}-{self._object.date_range_covered_start.strftime('%B')}"

    def _get_columns_export(self):
        self._columns = {
            "brand__name": "Brand",
            "sum_sale_charged": "Total Sales",
            "sum_cog": "COGS",
            "sum_actual_shipping_cost": "Actual Shipping Cost",
            "sum_estimated_shipping_cost": "Estimated Shipping Cost",
            "sum_profit": "Profit",
            "sum_margin": "Margin"
        }
        self._columns_as_type = {
            "brand__name": "string",
            "sum_sale_charged": "number",
            "sum_cog": "number",
            "sum_actual_shipping_cost": "number",
            "sum_estimated_shipping_cost": "number",
            "sum_profit": "number",
            "sum_margin": "string"
        }

    def _get_object(self) -> SPReportClient:
        return SPReportClient.objects.tenant_db_for(self._client_id).get(pk=self._object_id)

    def _get_date_range(self):
        tz_info = pytz.timezone(self._object.meta.get("time_zone", "UTC"))
        start_date = datetime.combine(self._object.date_range_covered_start, datetime.min.time())
        end_date = datetime.combine(self._object.date_range_covered_end, datetime.max.time())
        return [
            tz_info.localize(start_date).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S+00:00"),
            tz_info.localize(end_date).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S+00:00")
        ]

    def _get_queryset_base(self, sale_status):
        date_ranges = self._get_date_range()
        cond = Q(sale_date__gte=date_ranges[0], sale_date__lte=date_ranges[1], brand__isnull=False)
        if sale_status:
            cond.add(Q(sale_status__value__in=sale_status), Q.AND)
        return SaleItem.objects.tenant_db_for(self._client_id).filter(cond)

    def _get_queryset_data_covered(self, sheet_name: str, sale_status: List[str]) -> Union[QuerySet, None]:
        try:
            queryset = self._get_queryset_base(sale_status)
            assert queryset.count() > 0, f"Not Found Data {self._time_now.strftime('%b')} For Export"
            join_sale_status = str(tuple(sale_status)) if len(sale_status) > 1 else f"""('{sale_status[0]}')"""
            queryset = copy.deepcopy(SQL_PLAINTEXT)
            queryset = queryset.replace("$CLIENT_ID_DB$", self.client_id_db) \
                .replace("$SALE_DATE_FROM$", self.date_range[0]) \
                .replace("$SALE_DATE_TO$", self.date_range[1]) \
                .replace("$SALE_STATUS_ORDERS$", join_sale_status)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self._client_id}][_get_queryset_data_covered]"
                         f"[{sheet_name}]{sale_status} {ex}")
            queryset = None
        return queryset

    def normalize_item_data(self, item: any) -> List[Union[dict, None]]:
        try:
            val = item
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self._client_id}][{item}][normalize_item_data] {ex}")
            val = None
        return val

    def _init_header_file_report(self, file_path: str):
        workbook = Workbook(file_path)
        # Add a bold format to use to highlight cells.
        cell_format = workbook.add_format({
            'text_wrap': True,
            'bold': True,
            'font_size': 16,
            'bg_color': '#2ECC71',
            'align': 'center'
        })
        cells_format = {
            "brand__name": {
                "width": 22
            },
            "sum_sale_charged": {
                "width": 17
            },
            "sum_cog": {
                "width": 11
            },
            "sum_actual_shipping_cost": {
                "width": 18
            },
            "sum_estimated_shipping_cost": {
                "width": 18
            },
            "sum_profit": {
                "width": 11
            },
            "sum_margin": {
                "width": 12
            }
        }
        for sheet in self.__SHEETS_CONFIG__.keys():
            worksheet = workbook.add_worksheet(name=sheet)
            i = 0
            for k, v in self._columns.items():
                worksheet.set_column(i, i, cells_format[k]["width"])
                worksheet.write(0, i, v, cell_format)
                i += 1
        workbook.close()

    def process(self):
        try:
            for sheet, vals in self.__SHEETS_CONFIG__.items():
                queryset = self._get_queryset_data_covered(sheet, vals)
                if queryset is None:
                    logger.debug(f"[{self.__class__.__name__}][{self._client_id}][process][{sheet}]{vals} "
                                 f"Not found data for compute")
                    continue
                logger.info(f"[{self.__class__.__name__}][{self._client_id}][process][{sheet}]{vals} computing ...")
                logger.info(f"[{self.__class__.__name__}][{self._client_id}][process][{sheet}]{vals} "
                            f"SQL = {queryset}")
                self._export_schema.processing_data_frame(data=queryset, sheet_name=sheet)
            self.__save_object_completed()
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self._client_id}][process] Error {ex}"
            )
            self.__save_object_completed(
                status=ERROR_STATUS, log=str(ex),
                msg_error=dict(
                    code="System",
                    message="Please contact Administrator"
                )
            )

    def __save_object_completed(self, status: str = READY_STATUS, **kwargs):
        if status == READY_STATUS:
            url = self._export_schema.up_to_service(self._file_path)
            logger.debug(
                f"[{self.__class__.__name__}][{self._client_id}][__save_object_completed] download url = {url} ..."
            )
            self._object.download_urls = [url]
            self._object.date_completed = self._time_now
        self._object.status = status
        for k, v in kwargs.items():
            setattr(self._object, k, v)
        self._object.save()
