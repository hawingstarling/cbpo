from django.db.models import Q
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from app.core.services.user_permission import get_user_permission
from app.financial.jobs.bulk_process import bulk_handler
from app.database.helper import get_connection_workspace
import logging
import uuid
from abc import abstractmethod
from django.conf import settings
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from plat_import_lib_api.models import DataImportTemporary, PROCESSING, REVOKED, PROCESSED, FAILURE, REVERTING, \
    REVERTED, RawDataTemporary
from plat_import_lib_api.services.modules.base import BaseModule
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.context import AppContext
from app.core.exceptions import InvalidFormatException, InvalidParameterException
from app.financial.exceptions import RevertBulkSyncException
from app.financial.import_template.sale_item_bulk_edit import SaleItemBulkEdit
from app.financial.import_template.sale_item_bulk_sync import SaleItemBulkSync
from app.financial.models import SaleItem, DataFlattenTrack, FinancialSettings
from app.financial.permissions.base import JwtTokenPermission
from app.financial.permissions.sale_items import SaleItemBulkUpdatePermission, SaleItemBulkDeletePermission
from app.financial.services.activity import ActivityService
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_id_data_source_3rd_party, get_flatten_source_name
from app.financial.sub_serializers.bulk_base_serializer import BulkBaseSerializer, BulkDetailSerializer, \
    BulkSummarySerializer, BulkCreateSerializer, BulkListItemSerializer
from app.financial.sub_serializers.sale_item_bulk_edit_serializer import SaleItemBulkEditCreateSerializer
from app.financial.sub_serializers.sale_item_bulk_sync_serializer import SaleItemBulkSyncCreateSerializer
from app.financial.sub_serializers.user_serializer import UserSerializer
from app.financial.sub_views.brand_setting_view import BRAND_SETTING_MODULE_UPDATE_SALES
from app.financial.sub_views.client_view import SaleItemsBaseView
from app.financial.variable.activity_variable import BULK_EDIT_SALE_ITEM_DATA_KEY, BULK_DELETE_SALE_ITEM_DATA_KEY, \
    BULK_SYNC_SALE_ITEM_DATA_KEY, REVERT_BULK_EDIT_SALE_ITEM_DATA_KEY
from app.financial.variable.bulk_command_variable import BULK_COMMAND_CHOICE
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY
from app.job.utils.helper import revoked_category_job, register
from app.job.utils.variable import BULK_CATEGORY, MODE_RUN_IMMEDIATELY
from plat_import_lib_api.static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)

BULK_MODULES = (SaleItemBulkEdit.__NAME__, SaleItemBulkSync.__NAME__, BRAND_SETTING_MODULE_UPDATE_SALES)


class BulkBaseView(SaleItemsBaseView):
    serializer_class = BulkBaseSerializer
    client_id = None
    jwt_token = None
    user_id = None
    user_info = None
    sale_item_ids = []
    sale_item_query = None
    import_id = None

    def fetch_info_request(self):
        # Auth/Permission info
        self.jwt_token = AppContext.instance().jwt_token
        self.client_id = AppContext.instance().client_id
        self.user_id = AppContext.instance().user_id
        user_permission = get_user_permission(self.jwt_token, self.client_id, self.user_id)
        self.user_info = UserSerializer(user_permission.user).data


class BulkCreateView(BulkBaseView, CreateAPIView):
    @property
    @abstractmethod
    def module(self) -> BaseModule:
        pass

    @property
    @abstractmethod
    def command(self) -> str:
        pass

    @property
    @abstractmethod
    def activity_key(self) -> str:
        pass

    def verify_bulk_data_process_limit(self, total_request: int):
        try:
            limit_setting = FinancialSettings.objects.tenant_db_for(self.kwargs['client_id']).order_by(
                '-created').first().bulk_data_process_limit
        except Exception as ex:
            limit_setting = 5000
        if total_request > limit_setting:
            raise InvalidFormatException(
                message="The number of bulk processing data set by limit/threshold of max-capacity of the resource",
                verbose=True)

    def create(self, request, *args, **kwargs):
        try:
            validated_data = self.validate_request()
            self.fetch_info_request()
            # create bulk-item
            validated_data = self.create_bulk_data(meta=validated_data)
            serializer = self.validate_bulk_data(data=validated_data)
            serializer.save()
            data = serializer.data
            self.import_id = str(data['id'])
            self.start_processing(data)
            self.activity_log()
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            title = '[{class_name}] {ex}'.format(class_name=self.__class__.__name__, ex=ex)
            logger.error(title, exc_info=True)
            raise ex

    def validate_request(self):
        data = self.request.data
        # Should exist sale item filter or ids in the request
        if not data.get('query') and not data.get('ids'):
            raise InvalidFormatException(
                message="Missing/empty property from request body: <filter> or <ids>", verbose=True)
        return data

    def fetch_info_request(self):
        super().fetch_info_request()
        if self.activity_key == REVERT_BULK_EDIT_SALE_ITEM_DATA_KEY:
            return
            # Fetch ids or query for bulk processing
        data = self.request.data
        self.sale_item_ids = data.get('ids', [])
        self.sale_item_query = data.get('query', {})

        is_get_objs = True
        if 'filter' in self.sale_item_query:
            is_get_objs = False
            if self.sale_item_query.get('filter') == {}:
                self.sale_item_ids = ['__all__']
        if is_get_objs:
            self.get_objects(self.sale_item_ids)

    def create_bulk_data(self, meta):
        # create bulk-item
        meta['command'] = self.command
        meta['module'] = self.module.__NAME__
        meta['ids'] = self.sale_item_ids
        meta['query'] = self.sale_item_query
        meta['client_id'] = self.client_id
        meta['user_id'] = self.user_id
        meta['jwt_token'] = self.jwt_token
        meta['user_info'] = {key: self.user_info[key] for key in
                             ('avatar', 'email', 'first_name', 'last_name', 'fullname_search')}
        #
        if '__all__' in self.sale_item_ids:
            total = SaleItem.objects.tenant_db_for(self.client_id).count()
        else:
            total = len(self.sale_item_ids)
            if 'filter' in self.sale_item_query and self.sale_item_query.get('filter'):
                total += self.get_count_result_from_query(self.sale_item_query)
        #
        self.verify_bulk_data_process_limit(total)
        #
        summary = BulkSummarySerializer(data={'total': total})
        summary.is_valid(raise_exception=True)
        info_import_file = {'summary': summary.validated_data,
                            'cols_file': [{'name': 'id', 'label': 'Object ID'}],
                            'map_cols_to_module': [{'upload_col': 'id', 'target_col': 'id'}]}
        return {'client_id': self.client_id, 'module': self.module.__NAME__, 'info_import_file': info_import_file,
                'meta': meta}

    def validate_bulk_data(self, data):
        serializer = self.get_serializer(data=data, context=self.get_serializer_context())
        if not serializer.is_valid():
            raise InvalidFormatException(message=serializer.errors, verbose=True)
        return serializer

    def get_count_result_from_query(self, query: dict):
        data_source_tracking = DataFlattenTrack.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                                          type=FLATTEN_SALE_ITEM_KEY)
        table_name = get_flatten_source_name(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY)
        data_source_service = DataSource(client_id=self.client_id, type_flatten=FLATTEN_SALE_ITEM_KEY,
                                         table=table_name, access_token=settings.DS_TOKEN,
                                         api_centre=ApiCentreContainer.data_source_central(),
                                         source=data_source_tracking.source, token_type='DS_TOKEN')
        external_id = get_id_data_source_3rd_party(source=data_source_tracking.source, client_id=self.client_id,
                                                   type_flatten=FLATTEN_SALE_ITEM_KEY)
        fields = [
            {
                "name": "sale_item_id",
                "alias": "sale_item_id"
            }
        ]
        count_result = data_source_service.call_query(external_id=external_id, fields=fields, query_type='count',
                                                      **query)
        return int(count_result['count'])

    def start_processing(self, data, task_id: str = None):
        if task_id is None:
            task_id = str(data['id'])
        data_info = {
            "module": self.module.__NAME__,
            "jwt_token": self.jwt_token,
            "import_temp_id": data['id'],
            "client_id": self.client_id,
            "user_id": self.user_id
        }
        #
        client_db = get_connection_workspace(self.client_id)
        lib_import = DataImportTemporary.objects.db_manager(using=client_db).get(id=data['id'])
        lib_import.meta['task_id'] = task_id
        lib_import.save()
        #
        if plat_import_setting.use_queue:
            data = dict(
                task_id=task_id,
                client_id=self.client_id,
                name=f"bulk_handler_{task_id}",
                job_name="app.financial.jobs.bulk_process.bulk_handler",
                module="app.financial.jobs.bulk_process",
                method="bulk_handler",
                meta=data_info
            )
            transaction.on_commit(lambda: register(category=BULK_CATEGORY, mode_run=MODE_RUN_IMMEDIATELY, **data),
                                  using=client_db)
        else:
            bulk_handler(**data_info)

    def activity_log(self):
        ActivityService(client_id=self.client_id, user_id=self.user_id).create_activity_action_sale_data(
            self.activity_key, self.import_id)


class BulkListView(BulkBaseView, ListAPIView):
    serializer_class = BulkListItemSerializer
    module_param = openapi.Parameter('module', openapi.IN_QUERY, type=openapi.TYPE_STRING)

    status_param = openapi.Parameter('status', openapi.IN_QUERY,
                                     description="Bulk status going/done",
                                     type=openapi.TYPE_STRING)

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description='Search by information (user email, command, source)',
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = AppContext().instance().client_id
        cond = Q(module__in=BULK_MODULES, client_id=client_id)
        status_req = self.request.query_params.get('status')
        if status_req:
            cond &= Q(status=status_req)
        module_req = self.request.query_params.get('module')
        if module_req:
            cond &= Q(module=module_req)
        search = self.request.query_params.get('search')
        if search:
            search = search.strip().lower()
            cond &= (
                    Q(meta__user_info__email=search) |
                    Q(meta__command=search) |
                    Q(meta__sources=[f"{search.replace(' ', '_')}"]) |
                    Q(meta__user_info__fullname_search=search)
            )
        return DataImportTemporary.objects.db_manager(using=get_connection_workspace(client_id)) \
            .filter(cond).order_by('-modified', '-created')

    @swagger_auto_schema(manual_parameters=[status_param, module_param, search])
    @method_decorator(cache_page(10))
    @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)
        query_set = self.get_queryset()
        count_processing = query_set.filter(status=PROCESSING).count()
        response.data = {
            'count_processing': count_processing,
            **response.data
        }
        return response


class BulkActionTypeFilterView(APIView):
    permission_classes = (JwtTokenPermission,)

    def get(self, request, *args, **kwargs):
        data = {
            "status": [
                {
                    'key': PROCESSING,
                    'label': 'Processing'
                },
                {
                    'key': PROCESSED,
                    'label': 'Processed'
                },
                {
                    'key': FAILURE,
                    'label': 'Failure'
                },
                {
                    'key': REVOKED,
                    'label': 'Revoked'
                },
                {
                    'key': REVERTING,
                    'label': 'Reverting'
                },
                {
                    'key': REVERTED,
                    'label': 'Reverted'
                },
            ],
            "module": [
                {
                    'key': SaleItemBulkEdit.__NAME__,
                    'label': 'Bulk Edit'
                },
                {
                    'key': SaleItemBulkSync.__NAME__,
                    'label': 'Bulk Sync'
                },
                {
                    'key': BRAND_SETTING_MODULE_UPDATE_SALES,
                    'label': 'Updating Sales'
                }
            ]
        }
        return Response(status=status.HTTP_200_OK, data=data)


class BulkRetrieveView(BulkBaseView, RetrieveUpdateAPIView):
    serializer_class = BulkDetailSerializer

    def get_object(self):
        client_id = self.kwargs.get('client_id')
        client_db = get_connection_workspace(client_id)
        bulk_id = self.kwargs.get('pk')
        return DataImportTemporary.objects.db_manager(using=client_db).defer('json_data_last_cache').get(pk=bulk_id,
                                                                                                         client_id=client_id)


class SaleItemBulkEditCreateView(BulkCreateView):
    permission_classes = (SaleItemBulkUpdatePermission,)
    module = SaleItemBulkEdit
    command = BULK_COMMAND_CHOICE[0][0]
    activity_key = BULK_EDIT_SALE_ITEM_DATA_KEY

    @swagger_auto_schema(
        operation_description="""Create bulk edit sale items record by actions
            https://mayoretailinternetservices.atlassian.net/wiki/spaces/PF/pages/795246593/Bulk+Edit+of+Sale-items
            """,
        request_body=SaleItemBulkEditCreateSerializer,
        responses={200: BulkBaseSerializer})
    def post(self, request, *args, **kwargs):
        return self.create(request)

    def validate_request(self):
        # validate request body
        data = super().validate_request()
        serializer = SaleItemBulkEditCreateSerializer(data=data, context=self.get_serializer_context())
        if not serializer.is_valid():
            raise InvalidFormatException(message=serializer.errors)
        return data


class SaleItemRevertBulkEditCreateView(SaleItemBulkEditCreateView):
    permission_classes = [JwtTokenPermission]
    activity_key = REVERT_BULK_EDIT_SALE_ITEM_DATA_KEY

    def get_objects(self):
        pk = self.kwargs.get('pk')
        try:
            instance = DataImportTemporary.objects.db_manager(
                using=get_connection_workspace(self.kwargs.get('client_id'))) \
                .get(id=pk, module=SaleItemBulkEdit.__NAME__)
        except DataImportTemporary.DoesNotExist:
            raise Http404('No %s matches the given query.' % DataImportTemporary._meta.object_name)
        if instance.status == REVERTING:
            raise RevertBulkSyncException(message=f"Revert Bulk Edit still running ..")
        if instance.status == REVERTED:
            raise RevertBulkSyncException(message=f"Revert Bulk Edit already revert")
        if instance.status not in [PROCESSED, REVOKED]:
            raise RevertBulkSyncException(message=f"Revert Bulk Edit trigger accept status COMPLETED or CANCELLED")

        return instance

    @swagger_auto_schema(
        operation_description="""Create revert bulk edit sale items record by actions""", request_body=no_body,
        responses={200: BulkBaseSerializer})
    def post(self, request, *args, **kwargs):
        super().fetch_info_request()
        #
        instance = self.get_objects()
        __is_revoked = instance.status == REVOKED
        instance.status = REVERTING
        instance.progress = 0
        instance.info_import_file['summary'].update({
            'success': 0,
            'error': 0,
            'errors': []
        })
        instance.save()
        #
        data = self.get_serializer(instance).data
        task_id = None
        if __is_revoked:
            # because task_id set by id of lib import so when task id revoke worker celery tracking it's can't reactive
            # we need generate new id for task
            task_id = str(uuid.uuid4())
        self.import_id = str(instance.pk)
        self.start_processing(data, task_id)
        self.activity_log()
        return Response(status=status.HTTP_200_OK, data=data)


class SaleItemBulkDeleteCreateView(BulkCreateView):
    permission_classes = (SaleItemBulkDeletePermission,)
    module = SaleItemBulkEdit
    command = BULK_COMMAND_CHOICE[1][0]
    activity_key = BULK_DELETE_SALE_ITEM_DATA_KEY

    @swagger_auto_schema(
        operation_description="""Create bulk delete sale items record by actions
            https://mayoretailinternetservices.atlassian.net/wiki/spaces/PF/pages/795246593/Bulk+Edit+of+Sale-items
            """,
        request_body=BulkCreateSerializer,
        responses={200: BulkBaseSerializer})
    def post(self, request, *args, **kwargs):
        return self.create(request)

    def validate_request(self):
        # validate request body
        data = super().validate_request()
        serializer = BulkCreateSerializer(data=data)
        if not serializer.is_valid():
            raise InvalidFormatException(message=serializer.errors)
        return serializer.validated_data


class SaleItemBulkSyncCreateView(BulkCreateView):
    module = SaleItemBulkSync
    command = BULK_COMMAND_CHOICE[2][0]
    activity_key = BULK_SYNC_SALE_ITEM_DATA_KEY

    @swagger_auto_schema(
        operation_description="""Create bulk edit sale items record by actions
            https://mayoretailinternetservices.atlassian.net/wiki/spaces/PF/pages/795246593/Bulk+Edit+of+Sale-items
            """,
        request_body=SaleItemBulkSyncCreateSerializer,
        responses={200: BulkBaseSerializer})
    def post(self, request, *args, **kwargs):
        return self.create(request)

    def validate_request(self):
        # validate request body
        data = super().validate_request()
        serializer = SaleItemBulkSyncCreateSerializer(data=data)
        if not serializer.is_valid():
            raise InvalidFormatException(message=serializer.errors)
        return serializer.validated_data


class CancelBulkProgressView(APIView):
    permission_classes = (JwtTokenPermission,)

    def get_objects(self):
        bulk_progress_id = self.kwargs.get('bulk_progress_id')
        client_id = self.kwargs.get('client_id')
        client_db = get_connection_workspace(client_id)
        try:
            import_lib = DataImportTemporary.objects.db_manager(using=client_db) \
                .get(id=bulk_progress_id, client_id=client_id)
            return bulk_progress_id, import_lib
        except DataImportTemporary.DoesNotExist:
            raise InvalidParameterException(f'{bulk_progress_id} does not exist.')

    def activity_log_revoke(self, import_lib: DataImportTemporary):
        client_id = self.kwargs.get('client_id')
        user_id = AppContext.instance().user_id
        act_service = ActivityService(client_id=client_id, user_id=user_id)
        kwargs = dict(
            command=import_lib.meta.get('command'),
            sources=import_lib.meta.get('sources'),
            custom_report_type=import_lib.meta.get('custom_report_type')
        )
        act_service.create_activity_revoke_action(import_lib.module, self.kwargs.get('bulk_progress_id'), **kwargs)

    def put(self, request, *args, **kwargs):
        client_id = self.kwargs.get('client_id')
        client_db = get_connection_workspace(client_id)
        task_id, import_lib = self.get_objects()
        revoked_category_job(category=BULK_CATEGORY, task_ids=[task_id])

        with transaction.atomic():
            processing_errors = [{'code': 'revoked', 'message': "user's cancellation"}]
            RawDataTemporary.objects.db_manager(client_db) \
                .filter(lib_import_id=import_lib.pk, status=import_lib.status) \
                .update(status=REVOKED, processing_errors=processing_errors)
            import_lib.status = REVOKED
            import_lib.log = "user's cancellation"
            import_lib.progress = 100
            import_lib.save()
        self.activity_log_revoke(import_lib)
        return Response(status=status.HTTP_200_OK, data={"message": "cancelled"})
