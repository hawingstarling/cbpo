import logging
from django.utils import timezone
from rest_framework import status
from app.core.exceptions import ACServiceError
from app.core.helper import get_connections_client_channels
from app.core.services.ac_service import ACManager
from app.core.utils import convert_result_from_request_api
from app.core.variable.marketplace import SELLER_PARTNER_CONNECTION
from app.financial.models import Channel
from app.core.variable.sc_method import SPAPI_CONNECT_METHOD
from celery import current_app
from app.job.utils.helper import register_list
from app.job.utils.variable import SELLING_PARTNER_CATEGORY, MODE_RUN_PARALLEL
from app.selling_partner.jobs.report_brand_summary import handler_generate_sp_report_brands_summary_workspace
from app.selling_partner.models import SPReportClient, Setting
from app.selling_partner.variables.report_source import SPAPI_SOURCE_TYPE
from app.selling_partner.variables.report_status import READY_STATUS, IN_PROGRESS_STATUS, ERROR_STATUS, \
    MAX_REPORT_RETRY_DEFAULT, AC_SPAPI_REPORT_RETRY_CODE, CANCELLED_STATUS

logger = logging.getLogger(__name__)


@current_app.task(bind=True)
def register_sp_report_of_client(self, client_id: str, sp_report_id: str):
    logger.info(f"[{self.request.id}][{client_id}][register_sp_report_of_client][{sp_report_id}] Begin register ...")
    report = SPReportClient.objects.tenant_db_for(client_id).get(client_id=client_id, id=sp_report_id)
    handler_register_sp_report_of_client(client_id, report)
    report.save()


def handler_trigger_sp_report_clients(client_ids: []):
    jobs_data = list()
    for client_id in client_ids:
        marketplaces = Channel.objects.tenant_db_for(client_id).filter(is_pull_data=True).values_list('name', flat=True)
        client_connections = get_connections_client_channels(client_id, list(marketplaces), [SELLER_PARTNER_CONNECTION])
        qs = SPReportClient.objects.tenant_db_for(client_id).filter(client_id=client_id, status=IN_PROGRESS_STATUS)
        for marketplace in marketplaces:
            try:
                assert client_connections[SELLER_PARTNER_CONNECTION].get(marketplace, False) is True, \
                    f"The workspace doesn't connect marketplace"
            except Exception as ex:
                logger.error(f"[{client_id}[{marketplace}][handler_trigger_sp_report_clients] {ex}")
                qs.filter(channel__name=marketplace).update(
                    status=ERROR_STATUS,
                    msg_error={"code": "Unauthorized", "message": "Access to the resource is forbidden"}
                )
        if not qs.exists():
            logger.error(f"[handler_trigger_sp_report_clients][{client_id}] not found reports in progress status")
            continue
        data = dict(
            name=f"get_result_sp_reports_of_client_{client_id}",
            client_id=client_id,
            job_name="app.selling_partner.jobs.report.get_result_sp_reports_of_client",
            module="app.selling_partner.jobs.report",
            method="get_result_sp_reports_of_client",
            meta=dict(client_id=client_id)
        )
        jobs_data.append(data)
    if jobs_data:
        register_list(SELLING_PARTNER_CATEGORY, jobs_data, mode_run=MODE_RUN_PARALLEL)
        logger.info(f"[handler_trigger_sp_report_clients][{client_ids}] register_list app jobs completed")


def handler_register_sp_report_of_client(client_id: str, report: SPReportClient, is_retry: bool = False):
    logger.info(f"[{client_id}][handler_register_sp_report_of_client][{report.pk}] Begin register ...")
    data = dict(
        marketplace=report.channel.name,
        report_type=report.report_type.value
    )
    if report.report_type.is_date_range:
        data.update(
            dict(
                start_date=report.date_range_covered_start.strftime('%Y-%m-%d'),
                end_date=report.date_range_covered_end.strftime('%Y-%m-%d')
            )
        )
    payload_optional = report.report_type.meta.get("payload_optional", {})
    if payload_optional:
        data.update(payload_optional)

    rs = ACManager(client_id=client_id, read_timeout=60).request_sc_report(sc_method=SPAPI_CONNECT_METHOD, data=data)
    status_code, content = convert_result_from_request_api(rs)
    if status_code in [status.HTTP_200_OK]:
        report.ac_report_id = content.get("id")
        report.batch_ids = content.get("report_ids", [])
        if is_retry:
            report.retry += 1
            report.msg_error = {}
    else:
        report.log = str(content)
    logger.info(f"[{client_id}][handler_register_sp_report_of_client] status {status_code} , content {content}")


@current_app.task(bind=True)
def get_result_sp_reports_of_client(self, client_id: str):
    logger.info(f"[{self.request.id}][{client_id}][pick_jobs_get_result_sp_report_client] Begin ...")
    setting = Setting.objects.tenant_db_for(client_id).order_by('-created').first()
    max_report_retry = setting.max_report_retry if setting else MAX_REPORT_RETRY_DEFAULT
    queryset = SPReportClient.objects.tenant_db_for(client_id).filter(client_id=client_id, status=IN_PROGRESS_STATUS,
                                                                      modified__lte=timezone.now())
    ac_manager = ACManager(client_id=client_id)
    page = 1
    while True:
        if not queryset.exists():
            logger.info(f"[{client_id}][get_result_sp_report_of_client][{page}] not found")
            break
        reports = list(queryset.order_by('created')[:500])
        bulk_objs = []
        logger.info(f"[{client_id}][get_result_sp_report_of_client][{page}] total = {len(reports)}")
        for report in reports:
            try:
                if report.report_type.source == SPAPI_SOURCE_TYPE:
                    if not report.ac_report_id:
                        handler_register_sp_report_of_client(client_id=client_id, report=report)
                    else:
                        rs = ac_manager.status_sc_report(report_id=report.ac_report_id, sc_method=SPAPI_CONNECT_METHOD)
                        status_code, content = convert_result_from_request_api(rs)
                        if status_code in [status.HTTP_200_OK]:

                            report_ids = content.get("report_ids", [])
                            if not report.batch_ids and report_ids:
                                report.batch_ids = report_ids

                            status_rp_ac = content.get("status")
                            if status_rp_ac == "DONE":
                                report.status = READY_STATUS
                                report.download_urls = content.get("download_links", [])
                                report.file_names = content.get("file_names", [])
                                report.date_completed = content.get("generated_date")
                            elif status_rp_ac == "ERROR":
                                msg_error = content.get("error", {})
                                if msg_error.get(
                                        "code") == AC_SPAPI_REPORT_RETRY_CODE and report.retry < max_report_retry:
                                    handler_register_sp_report_of_client(client_id, report, is_retry=True)
                                else:
                                    report.status = ERROR_STATUS
                                    report.msg_error = msg_error
                            elif status_rp_ac == "CANCELLED":
                                report.status = CANCELLED_STATUS
                                report.msg_error = content.get("error", {})
                            else:
                                pass
                        elif status_code in [status.HTTP_400_BAD_REQUEST]:
                            handler_register_sp_report_of_client(client_id, report, is_retry=True)
                        else:
                            report.log = str(content)

                        logger.info(f"[{client_id}][get_result_sp_report_of_client] "
                                    f"status {rs.status_code} , content {rs.content.decode('utf-8')}")
                else:
                    if report.report_type.value == "BRANDS_SUMMARY_MONTHLY_DATA_REPORT":
                        handler_generate_sp_report_brands_summary_workspace(client_id=client_id,
                                                                            sp_report_client_id=report.pk)
                        continue
                    else:
                        report.status = CANCELLED_STATUS
            except Exception as ex:
                report.log = str(ex)
                logger.error(f"[{client_id}][get_result_sp_report_of_client] {ex}")
            report.modified = timezone.now()
            bulk_objs.append(report)
        SPReportClient.objects.tenant_db_for(client_id) \
            .bulk_update(bulk_objs,
                         fields=["ac_report_id", "batch_ids", "status", "download_urls", "file_names", "msg_error",
                                 "date_completed", "log", "retry", "modified"])
        page += 1


@current_app.task(bind=True)
def revoke_sp_report_of_client(self, client_id: str, sp_report_id: str):
    logger.info(f"[{self.request.id}][{client_id}][revoke_sp_report_of_client][{sp_report_id}] Begin ...")
    report = SPReportClient.objects.tenant_db_for(client_id).get(client_id=client_id, id=sp_report_id)
    rs = ACManager(client_id=client_id).cancelled_sc_report(report_id=report.ac_report_id,
                                                            sc_method=SPAPI_CONNECT_METHOD)
    status_code, content = convert_result_from_request_api(rs)
    if status_code not in [status.HTTP_200_OK]:
        raise ACServiceError(status_code=status_code, message=str(content))

    logger.info(f"[{client_id}][revoke_sp_report_of_client] "
                f"status {rs.status_code} , content {rs.content.decode('utf-8')}")
