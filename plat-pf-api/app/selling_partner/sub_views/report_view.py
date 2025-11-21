import logging
import maya
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from app.core.context import AppContext
from app.core.permissions.whilelist import SafeListPermission
from app.financial.exceptions import InvalidClientACException
from app.financial.models import ClientSettings
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch
from app.selling_partner.exceptions import ReportUniqueException
from app.selling_partner.models import SPReportCategory, SPReportType, SPReportClient
from app.selling_partner.sub_serializers.report_serializer import SPReportCategoriesSerializer, \
    SPReportTypeSerializer, SPReportClientSerializer, SPReportClientGenerateSerializer, StatSPReportClientSerializer
from app.selling_partner.variables.report_status import IN_PROGRESS_STATUS, READY_STATUS

logger = logging.getLogger(__name__)


class ListSPReportCategoriesView(generics.ListAPIView):
    serializer_class = SPReportCategoriesSerializer
    queryset = SPReportCategory.objects.all()
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value of profit status""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        query = SPReportCategory.objects.tenant_db_for(self.kwargs['client_id']).filter(parent__isnull=True)
        if search:
            query = query.filter(Q(name__icontains=search))
        return query.order_by('sort')

    @swagger_auto_schema(operation_description='Get list report categories', manual_parameters=[search])
    # @method_decorator(cache_page(60 * 60))
    # @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListSPReportTypesView(generics.ListAPIView):
    serializer_class = SPReportTypeSerializer
    queryset = SPReportType.objects.all()
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value of profit status""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        report_categories_id = self.kwargs.get('report_category_id')
        query = SPReportType.objects.tenant_db_for(self.kwargs['client_id']).all()
        if report_categories_id:
            query = query.filter(Q(category_id=report_categories_id))
        if search:
            query = query.filter(Q(name__icontains=search))
        return query.order_by('sort')

    @swagger_auto_schema(operation_description='Get list report categories', manual_parameters=[search])
    # @method_decorator(cache_page(60 * 60))
    # @method_decorator(vary_on_headers("x-ps-client-id", ))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListCreateSPReportsView(generics.ListCreateAPIView):
    serializer_class = SPReportClientSerializer
    queryset = SPReportClient.objects.all()
    permission_classes = [JwtTokenPermission]

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="""Channel by filter""",
                                type=openapi.TYPE_STRING)

    status = openapi.Parameter('status', in_=openapi.IN_QUERY,
                               description="""Status by value""",
                               type=openapi.TYPE_STRING)

    report_type = openapi.Parameter('report_type', in_=openapi.IN_QUERY,
                                    description="""Report Type by value""",
                                    type=openapi.TYPE_STRING)

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        search = self.request.query_params.get('search', None)
        channel = self.request.query_params.get('channel')
        status_report = self.request.query_params.get('status')
        report_type = self.request.query_params.get('report_type')

        cond = Q(client_id=client_id)

        if channel:
            cond &= Q(channel__name=channel)
        if status_report:
            cond &= Q(status=status_report)
        if report_type:
            cond &= Q(report_type__value=report_type)
        if search:
            cond &= Q(batch_ids__contains=[search])

        queryset = SPReportClient.objects.tenant_db_for(client_id).filter(cond)

        # Sort field
        sort_field = self.request.query_params.get('sort_field')
        if not sort_field:
            sort_field = "date_requested"
        elif sort_field == "report_type.name":
            sort_field = "report_type__name"
        elif sort_field == "date_range_covered":
            sort_field = "date_range_covered_start"
        else:
            pass
        # Sort direction
        sort_direction = self.request.query_params.get('sort_direction')
        if not sort_direction:
            sort_direction = "desc"
        sort_config = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
        order_by = [item.output_str_sorting for item in sort_config]

        return queryset.order_by(*order_by)

    @swagger_auto_schema(operation_description='Get list report categories',
                         manual_parameters=[channel, status, report_type, search, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @staticmethod
    def raise_exception_distinct_report(client_id, data_validated_gen):
        cond_find = Q(client_id=client_id, **data_validated_gen)
        cond_find_status = [IN_PROGRESS_STATUS]

        if data_validated_gen['report_type'].value not in ["GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2",
                                                           "BRANDS_SUMMARY_MONTHLY_DATA_REPORT"]:
            cond_find_status += [READY_STATUS]

        cond_find &= Q(status__in=cond_find_status)
        find_qs = SPReportClient.objects.tenant_db_for(client_id).filter(cond_find)
        if find_qs.exists():
            raise ReportUniqueException(message="Report is already existing.", verbose=True)

    def request_sp_report(self, request, *args, **kwargs):
        client_id = kwargs['client_id']
        setting, _ = ClientSettings.objects.tenant_db_for(client_id).get_or_create(client_id=client_id)
        if not setting.ac_spapi_enabled:
            raise InvalidClientACException(message="Client ID is not register SPAPI", verbose=True)
        #
        serializer_gen = SPReportClientGenerateSerializer(data=request.data)
        serializer_gen.is_valid(raise_exception=True)

        self.raise_exception_distinct_report(client_id, serializer_gen.validated_data)

        request.data['client'] = client_id
        request.data['status'] = IN_PROGRESS_STATUS
        request.data['ac_report_id'] = None
        request.data['batch_ids'] = []
        request.data['date_requested'] = timezone.now()
        request.data['date_completed'] = None
        request.data['msg_error'] = {}
        request.data['retry'] = 0
        request.data['meta'] = dict(time_zone=settings.DS_TZ_CALCULATE)
        request.data['creator'] = AppContext.instance().user_id

    @swagger_auto_schema(operation_description="create custom column profile for filter data source",
                         request_body=SPReportClientGenerateSerializer,
                         responses={HTTP_201_CREATED: SPReportClientSerializer})
    def post(self, request, *args, **kwargs):
        self.request_sp_report(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)


class StatsListSPReportCategoriesView(ListSPReportCategoriesView):
    permission_classes = [SafeListPermission]

    def get_queryset(self):
        search = self.request.query_params.get('search')
        query = SPReportCategory.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(parent__isnull=True)
        if search:
            query = query.filter(Q(name__icontains=search))
        return query.order_by('sort')

    @swagger_auto_schema(tags=["Stats Reports"], operation_description='Get list report categories',
                         manual_parameters=[ListSPReportCategoriesView.search])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatsListSPReportTypesView(ListSPReportTypesView):
    permission_classes = [SafeListPermission]

    def get_queryset(self):
        search = self.request.query_params.get('search')
        report_categories_id = self.kwargs.get('report_category_id')
        query = SPReportType.objects.tenant_db_for(DEFAULT_DB_ALIAS).all()
        if report_categories_id:
            query = query.filter(Q(category_id=report_categories_id))
        if search:
            query = query.filter(Q(name__icontains=search))
        return query.order_by('sort')

    @swagger_auto_schema(tags=["Stats Reports"],
                         operation_description='Get list report categories',
                         manual_parameters=[ListSPReportTypesView.search])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatSPReportCategoriesView(generics.ListAPIView):
    permission_classes = [SafeListPermission]
    serializer_class = StatSPReportClientSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value""",
                               type=openapi.TYPE_STRING)
    report_type = openapi.Parameter('report_type', in_=openapi.IN_QUERY,
                                    description="""Search by value of report type""",
                                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)
    report_date = openapi.Parameter('report_date', in_=openapi.IN_QUERY,
                                    description="""Search by value of report date""",
                                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)

    def get_queryset(self):
        cond = Q()
        search = self.request.query_params.get('search', None)
        if search:
            cond &= Q(batch_ids__contains=[search])
        report_date = self.request.query_params.get('report_date')
        if report_date:
            report_date = maya.parse(report_date).datetime().date()
            cond &= Q(date_requested__date=report_date)
        report_type = self.request.query_params.get('report_type')
        if report_type:
            cond &= Q(report_type__value=report_type)
        queryset = SPReportClient.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond) \
            .order_by('-date_requested')
        return queryset

    @swagger_auto_schema(tags=["Stats Reports"],
                         operation_description='Get list report categories',
                         manual_parameters=[search, report_type, report_date])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RevokeSPReportsView(APIView):
    serializer_class = SPReportClientSerializer
    permission_classes = [JwtTokenPermission]

    def get_object(self):
        client_id = self.kwargs["client_id"]
        rp_id = self.kwargs["id"]
        SPReportClient.objects.tenant_db_for(client_id)
        return get_object_or_404(SPReportClient, id=rp_id)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        SPReportClientSerializer(context=self.get_renderer_context()).revoke(obj)
        return Response(status=HTTP_200_OK)
