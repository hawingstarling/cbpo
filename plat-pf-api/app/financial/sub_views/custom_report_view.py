import logging
import uuid
from abc import ABC

from celery.states import REVOKED as CELERY_REVOKED
from django.db import transaction
from django.db.models import QuerySet
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from plat_import_lib_api.models import DataImportTemporary
from rest_framework import status
from app.financial.models import CustomReport
from app.financial.sub_views.base_view import CustomBaseListCreateAPIViewSerializer, \
    CustomBaseRetrieveUpdateDestroyView
from .bulk_view import SaleItemBulkEditCreateView, CancelBulkProgressView
from ..import_template.custom_report import SaleItemCustomReport
from ..permissions.base import JwtTokenPermission
from app.database.helper import get_connection_workspace
from ...job.services.inspect import JobInspectManage
from ..sub_serializers.bulk_base_serializer import BulkBaseSerializer
from ..sub_serializers.custom_view_serializer import CustomReportCreateSerializer, CustomReportSerializer
from ..variable.activity_variable import BULK_CUSTOM_REPORT_DATA_KEY
from ..variable.bulk_command_variable import BULK_COMMAND_CHOICE
from rest_framework.response import Response

from ..variable.report import REPORTING, REVOKED, ANALYSIS_CR_TYPE
from ...core.exceptions import InvalidFormatException

logger = logging.getLogger(__name__)


class CustomBaseReportBulkOperationView(SaleItemBulkEditCreateView):
    command = BULK_COMMAND_CHOICE[0][0]
    activity_key = BULK_CUSTOM_REPORT_DATA_KEY
    custom_report_data = {}
    module = SaleItemCustomReport
    custom_report_type = ANALYSIS_CR_TYPE

    @property
    def cr_type(self):
        try:
            cr_type = self.kwargs['cr_type']
        except Exception as ex:
            cr_type = self.custom_report_type
        return cr_type

    def init_bulk_lib(self):
        meta = {
            'ids': self.custom_report_data['item_ids'],
            'query': self.custom_report_data['ds_query'],
            'updates': self.custom_report_data['bulk_operations'],
            'custom_report_type': self.cr_type,
            'custom_report_columns': self.custom_report_data['columns'],
            'custom_report_file_temp': None
        }
        # create bulk-item
        data = self.create_bulk_data(meta=meta)
        serializer = BulkBaseSerializer(data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        instance = DataImportTemporary(**data)
        instance.id = self.custom_report_data['id']
        DataImportTemporary.objects.db_manager(
            using=get_connection_workspace(client_id=self.kwargs['client_id'])).bulk_create([instance])
        return instance

    def create_bulk_data(self, meta):
        data = super().create_bulk_data(meta)
        data.update({"status": REPORTING})
        return data

    def create_bulk_process(self):
        try:
            self.fetch_info_request()
            instance = self.init_bulk_lib()
            serializer = BulkBaseSerializer(instance, context=self.get_serializer_context())
            data = serializer.data
            task_id = None
            async_result_status = JobInspectManage().get_async_result_status(task_id=instance.pk)
            if async_result_status == CELERY_REVOKED:
                task_id = str(uuid.uuid4())
            self.start_processing(data, task_id)
            self.activity_log()
        except Exception as ex:
            title = '[{class_name}] {ex}'.format(class_name=self.__class__.__name__, ex=ex)
            logger.error(title, exc_info=True)
            raise ex

    def fetch_info_request(self):
        self.request.data.update({
            'ids': self.custom_report_data['item_ids'],
            'query': self.custom_report_data['ds_query']
        })
        super().fetch_info_request()

    def validate_request(self):
        data = self.request.data
        # Should exist sale item filter or ids in the request
        if not data.get('ds_query') and not data.get('item_ids'):
            raise InvalidFormatException(
                message="Missing/empty property from request body: <filter> or <ids>")
        return data


class CustomReportViewListCreateView(CustomBaseListCreateAPIViewSerializer, CustomBaseReportBulkOperationView,
                                             ABC):
    serializer_class = CustomReportSerializer
    custom_model = CustomReport
    queryset = CustomReport.objects.all()

    def get_queryset_order(self, query_set: QuerySet):
        query_set = query_set.filter(type=ANALYSIS_CR_TYPE).order_by('-created')
        return query_set

    @swagger_auto_schema(operation_description="create custom report profile for filter data source",
                         request_body=CustomReportCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomReportSerializer})
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            data = self.validate_request()
            data.update({
                'client': str(kwargs['client_id']),
                'user': str(kwargs['user_id']),
                'type': self.custom_report_type
            })
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            self.custom_report_data = serializer.data
            self.create_bulk_process()
            instance.refresh_from_db()
            data = self.get_serializer(instance).data
            #
            return Response(status=status.HTTP_201_CREATED, data=data)


class CustomReportRetrieveUpdateDestroyView(CustomBaseRetrieveUpdateDestroyView, CustomBaseReportBulkOperationView):
    serializer_class = CustomReportSerializer
    custom_model = CustomReport
    queryset = CustomReport.objects.all()

    def get_permissions(self):
        return [JwtTokenPermission()]

    def perform_update(self, serializer):
        serializer.save()
        # compared change and trigger recalculation report
        self.custom_report_data = serializer.data
        self.handler_create_bulk_process_report_update()

    def handler_create_bulk_process_report_update(self):
        client_id = self.kwargs['client_id']
        _find = DataImportTemporary.objects.db_manager(using=get_connection_workspace(client_id)) \
            .filter(pk=self.kwargs['pk'])
        if _find.exists():
            self.create_bulk_process()

    def init_bulk_lib(self):
        client_id = self.kwargs['client_id']
        instance = DataImportTemporary.objects.db_manager(using=get_connection_workspace(client_id)) \
            .get(pk=self.kwargs['pk'])
        if instance.meta['ids'] != self.custom_report_data['item_ids'] \
                or instance.meta['query'] != self.custom_report_data['ds_query'] \
                or instance.meta['updates'] != self.custom_report_data['bulk_operations']:
            instance.progress = 0
            instance.status = REPORTING
            instance.json_data_last_cache = '[]'
            instance.meta['custom_report_file_temp'] = None
            instance.meta['custom_report_columns'] = self.custom_report_data['columns']
            instance.meta['ids'] = self.custom_report_data['item_ids']
            instance.meta['query'] = self.custom_report_data['ds_query']
            instance.meta['updates'] = self.custom_report_data['bulk_operations']
            instance.save()
        return instance


class CancelCustomReportView(CancelBulkProgressView):

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        client_id = self.kwargs.get('client_id')
        try:
            instance = CustomReport.objects.tenant_db_for(client_id).get(client_id=client_id, pk=pk)
        except DataImportTemporary.DoesNotExist:
            raise Http404('No %s matches the given query.' % DataImportTemporary._meta.object_name)
        with transaction.atomic():
            instance.status = REVOKED
            instance.save()
            self.kwargs.update({'bulk_progress_id': instance.id})
            return super().put(request, *args, **kwargs)
