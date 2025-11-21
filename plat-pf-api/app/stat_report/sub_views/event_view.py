from django.db import DEFAULT_DB_ALIAS
from django.db.models import Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.permissions.whilelist import SafeListPermission
from app.financial.models import Channel
from app.financial.sub_serializers.client_serializer import ChannelSerializer
from app.stat_report.models import StatClientChannelReport, StatReport
# from app.stat_report.services.stat_report import StatReporter
from app.stat_report.sub_serializers.event_serializer import StatReportSerializer, StatOrgClientReportSerializer


class StatReportSummaryView(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = StatReportSerializer

    @swagger_auto_schema(tags=["Stats Reports"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        obj = StatReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).first()
        data = StatReportSerializer(obj).data
        # data = StatReporter.calculation_for_stat_report_summary()
        return Response(data)


class StatOrgClientReportView(ListAPIView):
    permission_classes = [SafeListPermission]
    serializer_class = StatOrgClientReportSerializer

    org_id = openapi.Parameter('org_id', in_=openapi.IN_QUERY,
                               description="""Org Id""",
                               type=openapi.TYPE_STRING)

    client_id = openapi.Parameter('client_id', in_=openapi.IN_QUERY,
                                  description="""Client Id""",
                                  type=openapi.TYPE_STRING)

    channel = openapi.Parameter('channel', in_=openapi.IN_QUERY,
                                description="Channel name",
                                type=openapi.TYPE_STRING)

    report_type = openapi.Parameter('report_type', in_=openapi.IN_QUERY,
                                    description="""Report Type""",
                                    type=openapi.TYPE_STRING)

    status = openapi.Parameter('status', in_=openapi.IN_QUERY,
                               description="""status""",
                               type=openapi.TYPE_BOOLEAN)

    service = openapi.Parameter('service', in_=openapi.IN_QUERY,
                                description="""service""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        cond = Q()
        org_id = self.request.query_params.get('org_id')
        if org_id:
            cond = cond.add(Q(organization_id=org_id), Q.AND)
        client_id = self.request.query_params.get('client_id')
        if client_id:
            cond = cond.add(Q(client_id=client_id), Q.AND)
        channel = self.request.query_params.get('channel')
        if channel:
            cond = cond.add(Q(channel__name=channel), Q.AND)
        report_type = self.request.query_params.get('report_type')
        if report_type:
            cond = cond.add(Q(report_type=report_type), Q.AND)
        status = self.request.query_params.get('status')
        if status is not None:
            try:
                status = bool(eval(status.title()))
                if status is False:
                    cond = cond.add(Q(total_time_control_completed__lt=F('total_time_control')), Q.AND)
                else:
                    cond = cond.add(Q(total_time_control_completed=F('total_time_control')), Q.AND)
            except Exception as ex:
                pass
        qs = StatClientChannelReport.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).order_by('-report_date')
        return qs

    @swagger_auto_schema(tags=["Stats Reports"], operation_description='Get list org clients healthy',
                         manual_parameters=[org_id, client_id, channel, report_type, status, service])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatReportChannelView(ListAPIView):
    permission_classes = [SafeListPermission]
    serializer_class = ChannelSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search name channel""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        search = self.request.query_params.get('search')
        cond = Q(use_in_global_filter=True, is_pull_data=True)
        if search:
            cond &= (Q(name__icontains=search) | Q(label__icontains=search))
        return Channel.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).order_by('name')

    @swagger_auto_schema(tags=["Stats Reports"], operation_description='Get list channel report',
                         manual_parameters=[search])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
