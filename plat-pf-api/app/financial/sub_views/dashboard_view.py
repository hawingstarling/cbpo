import logging
from distutils.util import strtobool

from django.db.models import Q
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.context import AppContext
from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.exceptions import DivisionMaxLimitException
from app.financial.models import ClientDashboardWidget, DivisionClientUserWidget, DivisionManage, FinancialSettings, \
    SaleItem
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch
from app.financial.sub_serializers.dashboard_serializer import BulkDivisionUserWidgetSettingSerializer, \
    ClientDashboardWidgetSerializer, \
    BulkClientDashboardWidgetSerializer, BulkDivisionClientUserWidgetSerializer, DivisionUserWidgetSettingSerializer
from app.financial.variable.segment_variable import DIVISION_CATEGORY, DIVISION_CONFIG_CALCULATE_DEFAULT

logger = logging.getLogger(__name__)


class ListClientWidgetView(generics.ListAPIView):
    serializer_class = ClientDashboardWidgetSerializer
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value""",
                               type=openapi.TYPE_STRING)

    enabled = openapi.Parameter('enabled', in_=openapi.IN_QUERY,
                                description="""Enabled/Disabled filter""",
                                type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        search = self.request.query_params.get('search')
        # enabled
        enabled = self.request.query_params.get("enabled", None)

        cond = Q(client_id=client_id, widget__dashboard__key=dashboard)

        if enabled is not None:
            cond &= Q(enabled=bool(strtobool(enabled)))

        if search:
            cond &= Q(widget__key__icontains=search) | Q(widget__value__icontains=search)

        # Sorting
        sort_field = self.request.query_params.get('sort_field')
        if sort_field:
            sort_direction = self.request.query_params.get('sort_direction', 'asc')
            sort = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
        else:
            sort = [ISortConfigPostgresFulltextSearch(field_name='position', direction='asc')]
        order_by = [item.output_str_sorting for item in sort]

        queryset = ClientDashboardWidget.objects.tenant_db_for(client_id) \
            .filter(cond).order_by(*order_by)

        return queryset

    @swagger_auto_schema(operation_description='Get list widgets of dashboard',
                         manual_parameters=[search, enabled, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateClientWidgetView(APIView):
    serializer_class = ClientDashboardWidgetSerializer
    permission_classes = [JwtTokenPermission]

    def validate(self, validated_data):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        data = validated_data["data"]
        widget_keys = [item['widget'] for item in data]

        qs = ClientDashboardWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, widget__dashboard__key=dashboard, widget__key__in=widget_keys)

        widget_verifying = set(widget_keys) - set(qs.values_list('widget__key', flat=True)) == set()
        assert widget_verifying is True, "Payload widget key invalid, Please check again"

        return data

    def update_widget_keys(self, data):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        objs = []

        for item in data:
            obj = ClientDashboardWidget.objects.tenant_db_for(client_id).get(client_id=client_id,
                                                                             widget__dashboard__key=dashboard,
                                                                             widget__key=item["widget"])
            if "enabled" in item:
                obj.enabled = item["enabled"]
            if "position" in item:
                obj.position = item["position"]
            if "settings" in item:
                obj.settings = item["settings"]
            obj.modified = timezone.now()
            objs.append(obj)

        ClientDashboardWidget.objects.tenant_db_for(client_id).bulk_update(objs,
                                                                           fields=["enabled", "position", "settings",
                                                                                   "modified"])

    @swagger_auto_schema(
        operation_description='Widget manage update',
        request_body=BulkClientDashboardWidgetSerializer,
        responses={status.HTTP_200_OK: None})
    def put(self, request, *args, **kwargs):
        serializer = BulkClientDashboardWidgetSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        #
        data = self.validate(data)
        self.update_widget_keys(data)
        return Response(status=status.HTTP_200_OK)


class DivisionClientUserWidgetView(APIView):
    permission_classes = [JwtTokenPermission]

    def sync_division_manage_to_user(self):
        client_id = self.kwargs.get('client_id')
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        divisions = SaleItem.objects.tenant_db_for(client_id) \
            .filter(sale__channel__name=CHANNEL_DEFAULT, client_id=client_id, product_type__isnull=False) \
            .values_list('product_type', flat=True).distinct()
        objs = []
        for division in divisions:
            try:
                obj = DivisionClientUserWidget(
                    client_id=client_id,
                    category=category,
                    key=division,
                    name=division,
                    enabled=False,
                    settings=DIVISION_CONFIG_CALCULATE_DEFAULT
                )
                objs.append(obj)
            except Exception as ex:
                logger.debug(ex)
        if objs:
            DivisionClientUserWidget.objects.tenant_db_for(client_id).bulk_create(objs, ignore_conflicts=True)

    def get_data(self):
        client_id = self.kwargs.get("client_id")
        user_id = AppContext.instance().user_id
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        cond = Q(client_id=client_id, category=category)
        queryset = DivisionClientUserWidget.objects.tenant_db_for(client_id).filter(cond)
        if queryset.count() == 0:
            self.sync_division_manage_to_user()
        if category == DIVISION_CATEGORY:
            queryset = queryset.order_by('position', 'key')
        else:
            queryset = queryset.order_by('position')
        return list(queryset.values('key', 'name', 'enabled'))

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK, data=self.get_data())


class UpdateDivisionClientUserWidgetView(APIView):
    permission_classes = [JwtTokenPermission]

    def validate(self, validated_data):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        category = self.kwargs.get('category', DIVISION_CATEGORY)

        data = validated_data["data"]
        segments = [item['segment'] for item in data]

        qs = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, key__in=segments, category=category)

        assert qs.count() <= len(segments), "Payload segment key invalid, Please check again"

        return data

    def update_widget_keys(self, data):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        category = self.kwargs.get('category', DIVISION_CATEGORY)

        objs_inserts = []
        objs_updates = []

        for item in data:
            try:
                obj = DivisionClientUserWidget.objects.tenant_db_for(client_id).get(client_id=client_id,
                                                                                    category=category,
                                                                                    key=item["segment"])
                obj.enabled = item["enabled"]
                obj.modified = timezone.now()
                objs_updates.append(obj)
            except DivisionClientUserWidget.DoesNotExist:
                obj = DivisionClientUserWidget(
                    client_id=client_id,
                    category=category,
                    key=item["segment"],
                    enabled=item["enabled"]
                )
                objs_inserts.append(obj)
            except Exception as ex:
                logger.error(ex)

        if objs_inserts:
            DivisionClientUserWidget.objects.tenant_db_for(client_id).bulk_create(objs_inserts)
        if objs_updates:
            DivisionClientUserWidget.objects.tenant_db_for(client_id).bulk_update(objs_updates,
                                                                                  fields=["enabled", "modified"])

    @swagger_auto_schema(
        operation_description='Widget manage update',
        request_body=BulkDivisionClientUserWidgetSerializer,
        responses={status.HTTP_200_OK: None})
    def put(self, request, *args, **kwargs):
        serializer = BulkDivisionClientUserWidgetSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        #
        data = self.validate(data)
        self.update_widget_keys(data)
        return Response(status=status.HTTP_200_OK)


class SettingsDivisionClientUserWidgetView(APIView):
    permission_classes = [JwtTokenPermission]

    def sync_division_manage_to_user(self):
        client_id = self.kwargs.get('client_id')
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        divisions = DivisionManage.objects.tenant_db_for(client_id).filter(category=category, is_active=True)
        objs = []
        for item in divisions:
            try:
                objs.append(
                    DivisionClientUserWidget(client_id=client_id, category=category, key=item.key, name=item.name))
            except Exception as ex:
                logger.debug(ex)
        if objs:
            DivisionClientUserWidget.objects.tenant_db_for(client_id).bulk_create(objs, ignore_conflicts=True)

    def get_data(self):
        client_id = self.kwargs.get("client_id")
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        cond = Q(client_id=client_id, category=category)
        queryset = DivisionClientUserWidget.objects.tenant_db_for(client_id).filter(cond)
        if queryset.count() == 0:
            self.sync_division_manage_to_user()
        setting = FinancialSettings.objects.tenant_db_for(client_id).first()
        return {
            "division_max_limit": getattr(setting, "division_max_limit", 5),
            "data": list(queryset.values('key', 'name', 'sync_option', 'ytd_target_manual', 'ytd_max_manual',
                                         'mtd_target_manual', 'mtd_max_manual', 'enabled'))
        }

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK, data=self.get_data())

    @swagger_auto_schema(
        operation_description='Widget manage update',
        request_body=DivisionUserWidgetSettingSerializer,
        responses={status.HTTP_200_OK: None})
    def put(self, request, *args, **kwargs):
        client_id = self.kwargs.get("client_id")
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        serializer = DivisionUserWidgetSettingSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        #
        key = data.pop("key")
        obj = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
            .get(client_id=client_id, category=category, key=key)
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save()
        return Response(status=status.HTTP_200_OK)


class BulkSyncDivisionClientUserWidgetView(APIView):
    permission_classes = [JwtTokenPermission]

    def update_widget_keys(self, data):
        client_id = self.kwargs.get('client_id')
        dashboard = self.kwargs.get('dashboard')
        category = self.kwargs.get('category', DIVISION_CATEGORY)
        setting = FinancialSettings.objects.tenant_db_for(client_id).first()

        keys = [item.get("key") for item in data]
        keys_enabled = [item.get("key") for item in data if item.get("enabled") is True]
        if getattr(setting, "division_max_limit", 5) < len(keys_enabled):
            raise DivisionMaxLimitException("Division max limit is reached")

        for item in data:
            try:
                key = item.pop("key")
                obj, _ = DivisionClientUserWidget.objects.tenant_db_for(client_id) \
                    .update_or_create(client_id=client_id,
                                      category=category,
                                      key=key,
                                      defaults=item)
            except Exception as ex:
                logger.error(ex)
        # Delete not exist key
        cond = Q(client_id=client_id, category=category) & ~Q(key__in=keys)
        DivisionClientUserWidget.objects.tenant_db_for(client_id).filter(cond).delete()

    @swagger_auto_schema(
        operation_description='Widget manage update',
        request_body=BulkDivisionUserWidgetSettingSerializer,
        responses={status.HTTP_200_OK: None})
    def put(self, request, *args, **kwargs):
        serializer = BulkDivisionUserWidgetSettingSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        #
        self.update_widget_keys(data["data"])
        return Response(status=status.HTTP_200_OK)
