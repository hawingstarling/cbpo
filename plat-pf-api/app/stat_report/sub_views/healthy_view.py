from django.db.models import Q
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from app.core.permissions.whilelist import SafeListPermission
from app.stat_report.sub_serializers.health_serializer import OrgClientHealthySerializer
from app.stat_report.models import OrgClientHealth
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from app.stat_report.variables.healthy import SERVICE_CONFIG


class CheckServicesStatusView(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = OrgClientHealthySerializer

    @swagger_auto_schema(tags=["Services status"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        data = OrgClientHealth.summary_service_status()
        return Response(data)


class StatHealthySummaryView(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = OrgClientHealthySerializer

    @swagger_auto_schema(tags=["Stats Reports"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        data = OrgClientHealth.summary()
        return Response(data)


class StatOrgClientView(ListAPIView):
    permission_classes = [SafeListPermission]
    serializer_class = OrgClientHealthySerializer

    org_id = openapi.Parameter('org_id', in_=openapi.IN_QUERY,
                               description="""Org Id""",
                               type=openapi.TYPE_STRING)

    client_id = openapi.Parameter('client_id', in_=openapi.IN_QUERY,
                                  description="""Client Id""",
                                  type=openapi.TYPE_STRING)

    status = openapi.Parameter('status', in_=openapi.IN_QUERY,
                               description="""status""",
                               type=openapi.TYPE_BOOLEAN)

    service = openapi.Parameter('service', in_=openapi.IN_QUERY,
                                description="""service""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        cond = Q(is_enabled=True)
        org_id = self.request.query_params.get('org_id')
        if org_id:
            cond = cond & Q(organization_id=org_id)
        client_id = self.request.query_params.get('client_id')
        if client_id:
            cond = cond & Q(client_id=client_id)
        status = self.request.query_params.get('status')
        if status is not None:
            cond = cond & Q(is_healthy=bool(eval(status.title())))
        service = self.request.query_params.get('service')
        if service:
            cond = cond & Q(service_name=service)
        qs = OrgClientHealth.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).order_by('client__name')
        return qs

    @swagger_auto_schema(tags=["Stats Reports"], operation_description='Get list org clients healthy',
                         manual_parameters=[org_id, client_id, status, service])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StatHealthyStatus(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = OrgClientHealthySerializer

    @swagger_auto_schema(tags=["Stats Reports"])
    def get(self, request, *args, **kwargs):
        data = {
            True: 'Good',
            False: 'Fail'
        }
        return Response(data)


class StatHealthyService(APIView):
    permission_classes = [SafeListPermission]
    serializer_class = OrgClientHealthySerializer

    @swagger_auto_schema(tags=["Stats Reports"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return Response(SERVICE_CONFIG)
