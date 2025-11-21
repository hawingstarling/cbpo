from secrets import token_hex
import logging
from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from app.core.context import AppContext
from app.core.exceptions import InvalidFormatException
from app.financial.permissions.fedex_shipment_permissions import ViewFedExShipmentPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import generics, status
from app.financial.models import CustomReport, FedExShipment
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.fedex_shipment.utils import get_query_set_filter_shipping_invoice, \
    get_query_set_filter_shipping_invoice_transaction, get_shipping_invoice_trans_matched_sales_ids
from app.financial.sub_serializers.custom_view_serializer import CustomReportSerializer, \
    CustomReportSlugCreateSerializer
from app.financial.sub_serializers.fedex_shipment_serializer import FedExShipmentSerializer
from app.financial.sub_views.custom_report_view import CustomBaseReportBulkOperationView
from app.financial.variable.report import SHIPPING_INVOICE_CR_TYPE, SHIPPING_INVOICE_TRANS_CR_TYPE, \
    SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE, REPORTING

logger = logging.getLogger(__name__)


class ListShippingInvoiceTransView(generics.ListAPIView):
    serializer_class = FedExShipmentSerializer
    permission_classes = (ViewFedExShipmentPermission,)

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)
    status = openapi.Parameter('status', in_=openapi.IN_QUERY,
                               description="""Status filter""",
                               type=openapi.TYPE_STRING)
    source = openapi.Parameter('source', in_=openapi.IN_QUERY,
                               description="""Source filter""",
                               type=openapi.TYPE_STRING)

    from_date = openapi.Parameter('from_date', in_=openapi.IN_QUERY,
                                  description="""From date invoice""",
                                  type=openapi.TYPE_STRING)
    to_date = openapi.Parameter('to_date', in_=openapi.IN_QUERY,
                                description="""To date invoice""",
                                type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[source, from_date, to_date, status, keyword, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        shipping_invoice_id = self.kwargs.get('shipping_invoice_id')
        status = self.request.query_params.get('status')
        source = self.request.query_params.get('source')
        sort_field = self.request.query_params.get('sort_field')
        if not sort_field:
            sort_field = 'transaction_id'
        sort_direction = self.request.query_params.get('sort_direction')
        if not sort_direction:
            sort_direction = 'asc'
        keyword = self.request.query_params.get('keyword')
        queryset = get_query_set_filter_shipping_invoice_transaction(client_id=client_id,
                                                                     shipping_invoice_id=shipping_invoice_id,
                                                                     status=status, source=source,
                                                                     sort_field=sort_field,
                                                                     sort_direction=sort_direction,
                                                                     keyword=keyword)
        return queryset


class ListTransMatchedSalesView(APIView):
    permission_classes = [ViewFedExShipmentPermission]

    def get(self, request, *args, **kwargs):
        client_id = self.kwargs.get('client_id')
        shipping_invoice_id = self.kwargs.get('shipping_invoice_id')
        sale_ids = get_shipping_invoice_trans_matched_sales_ids(client_id, shipping_invoice_id)
        data = {
            'sale_ids': sale_ids
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomReportShippingInvoiceCreateView(CustomBaseReportBulkOperationView):
    permission_classes = [JwtTokenPermission]
    serializer_class = CustomReportSerializer
    custom_model = CustomReport
    queryset = CustomReport.objects.all()
    custom_report_type = SHIPPING_INVOICE_CR_TYPE

    def validate_request(self):
        data = self.request.data
        ids = data.get('item_ids', [])
        bulk_operations = data.get('bulk_operations', [])
        if not bulk_operations and not ids:
            raise InvalidFormatException(
                message="Missing/empty property from request body: <item_ids>/<bulk operation>")
        try:
            update_operations = {update['column']: update for update in bulk_operations}
            client_id = self.kwargs['client_id']
            from_date = update_operations.get('from_date', {}).get('value', None)
            to_date = update_operations.get('to_date', {}).get('value', None)
            status_invoice = update_operations.get('status', {}).get('value', None)
            source = update_operations.get('source', {}).get('value', None)
            keyword = update_operations.get('keyword', {}).get('value', None)
            queryset = get_query_set_filter_shipping_invoice(client_id=client_id, ids=ids, from_date=from_date,
                                                             to_date=to_date, status=status_invoice, source=source,
                                                             keyword=keyword)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            raise InvalidFormatException(
                message="From/to date request invalid format")
        if queryset.count() == 0:
            raise InvalidFormatException(
                message="From/To date request filter the invoice date not found data or missing/empty tracking id. Please import update and try again")
        return data

    def get_objects(self, sale_item_ids):
        return True

    @property
    def get_name_file(self):
        time_now = timezone.now()
        return f'Precise-Ship-Breaks-{time_now.strftime("%m-%d-%Y")}-{token_hex(6)}'

    @swagger_auto_schema(operation_description="create custom report shipping invoice profile for filter data source",
                         request_body=CustomReportSlugCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomReportSerializer})
    def post(self, request, *args, **kwargs):
        user_id = AppContext.instance().user_id
        with transaction.atomic():
            data = self.validate_request()
            data.update({
                'client': str(kwargs['client_id']),
                'user': str(user_id),
                'type': self.cr_type,
                'name': self.get_name_file
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


class CustomReportShippingInvoiceTransCreateView(CustomReportShippingInvoiceCreateView):
    custom_report_type = SHIPPING_INVOICE_TRANS_CR_TYPE

    def validate_request(self):
        data = self.request.data
        ids = data.get('item_ids', [])
        bulk_operations = data.get('bulk_operations', [])
        if not bulk_operations and not ids:
            raise InvalidFormatException(
                message="Missing/empty property from request body: <item_ids>/<bulk operation>")
        try:
            update_operations = {update['column']: update for update in bulk_operations}
            client_id = self.kwargs['client_id']
            shipping_invoice_id = update_operations.get('shipping_invoice_id', {}).get('value', None)
            status_trans = update_operations.get('status', {}).get('value', None)
            source = update_operations.get('source', {}).get('value', None)
            keyword = update_operations.get('keyword', {}).get('value', None)
            queryset = get_query_set_filter_shipping_invoice_transaction(client_id=client_id,
                                                                         ids=ids,
                                                                         shipping_invoice_id=shipping_invoice_id,
                                                                         status=status_trans, source=source,
                                                                         keyword=keyword)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            raise InvalidFormatException(
                message="Shipping Invoice ID date request invalid format")
        if queryset.count() == 0:
            raise InvalidFormatException(
                message="Shipping Invoice ID date request filter not found data or missing/empty tracking id. Please import update and try again")
        return data

    @swagger_auto_schema(
        operation_description="create custom report shipping invoices trans profile for filter data source",
        request_body=CustomReportSlugCreateSerializer,
        responses={status.HTTP_201_CREATED: CustomReportSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomReportShippingInvoiceTransUnmatchedInfoCreateView(CustomReportShippingInvoiceCreateView):
    custom_report_type = SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE

    @property
    def get_name_file(self):
        time_now = timezone.now()
        return f'Precise-Ship-Unmatched-Transactions-{time_now.strftime("%m-%d-%Y")}-{token_hex(6)}'

    def __find_instance_processing(self):
        client_id = self.kwargs['client_id']
        bulk_operations = self.request.data.get('bulk_operations', [])
        if not bulk_operations or len(bulk_operations) > 1:
            raise InvalidFormatException(
                message="Missing/empty property from request body: <bulk operation>")
        # validate custom report exist
        _find_qs = CustomReport.objects.tenant_db_for(client_id).filter(
            client_id=client_id,
            type=SHIPPING_INVOICE_TRANS_UNMATCHED_CR_TYPE,
            bulk_operations=bulk_operations, status=REPORTING)

        if _find_qs.exists():
            return _find_qs.order_by('-created').first()

        update_operations = {update['column']: update for update in bulk_operations}
        shipping_invoice_id = update_operations.get('shipping_invoice_id', {}).get('value', None)
        if not shipping_invoice_id:
            raise InvalidFormatException(
                message="Missing/empty property shipping invoice id from request body: <bulk operation>")
        # Validate shipping invoice trans exist data
        queryset = FedExShipment.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, shipping_invoice_id=shipping_invoice_id)
        if queryset.count() == 0:
            raise InvalidFormatException(
                message="Shipping Invoice ID date request filter not found data or missing/empty shipping invoice id. "
                        "Please import update and try again")
        return None

    def validate_request(self):
        return self.request.data

    @swagger_auto_schema(
        operation_description="create custom report shipping invoices trans unmatched",
        request_body=CustomReportSlugCreateSerializer,
        responses={status.HTTP_201_CREATED: CustomReportSerializer})
    def post(self, request, *args, **kwargs):
        instance = self.__find_instance_processing()
        if instance:
            data = self.get_serializer(instance).data
            #
            return Response(status=status.HTTP_201_CREATED, data=data)
        return super().post(request, *args, **kwargs)
