import logging
from secrets import token_hex
from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from app.core.context import AppContext
from app.core.exceptions import InvalidFormatException
from app.extensiv.utils import get_query_set_filter_cogs_conflict
from app.financial.services.fedex_shipment.utils import get_query_set_filter_shipping_invoice, \
    get_query_set_filter_shipping_invoice_transaction
from app.financial.services.item.utils import get_query_set_filter_items
from app.financial.services.top_asins.utils import get_query_set_filter_top_asins
from app.financial.sub_serializers.custom_view_serializer import CustomReportSerializer, \
    CustomReportSlugCreateSerializer
from app.financial.sub_views.custom_report_view import CustomReportViewListCreateView, \
    CustomReportRetrieveUpdateDestroyView, CancelCustomReportView
from app.financial.variable.report import SHIPPING_INVOICE_CR_TYPE, ANALYSIS_CR_TYPE, SHIPPING_INVOICE_TRANS_CR_TYPE, \
    ITEMS_CR_TYPE, TOP_ASINS_CR_TYPE, COGS_CONFLICT_CR_TYPE

logger = logging.getLogger(__name__)


class CustomReportDynamicViewListCreateView(CustomReportViewListCreateView):

    def get_queryset_filter_by_type(self, **filters):
        kwargs = {
            SHIPPING_INVOICE_CR_TYPE: get_query_set_filter_shipping_invoice,
            SHIPPING_INVOICE_TRANS_CR_TYPE: get_query_set_filter_shipping_invoice_transaction,
            ITEMS_CR_TYPE: get_query_set_filter_items,
            TOP_ASINS_CR_TYPE: get_query_set_filter_top_asins,
            COGS_CONFLICT_CR_TYPE: get_query_set_filter_cogs_conflict,
        }
        try:
            queryset = kwargs[self.cr_type](**filters)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][get_queryset_filter_by_type] {ex}")
            queryset = None
        return queryset

    def validate_request_by_ds_query(self):
        data = self.request.data
        # Should exist sale item filter or ids in the request
        if not data.get('ds_query') and not data.get('item_ids'):
            raise InvalidFormatException(
                message="Missing/empty property from request body: <filter> or <ids>")
        return data

    def validate_request_by_model_filter(self):
        data = self.request.data
        ids = data.get('item_ids', [])
        bulk_operations = data.get('bulk_operations', [])
        if not bulk_operations and not ids:
            raise InvalidFormatException(
                message="Missing/empty property from request body: <item_ids>/<bulk operation>")
        try:
            update_operations = {
                update['column']: update['value'] for update in bulk_operations}
            client_id = self.kwargs['client_id']
            queryset = self.get_queryset_filter_by_type(
                client_id=client_id, ids=ids, **update_operations)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            raise InvalidFormatException(
                message="From/to date request invalid format")
        if queryset.count() == 0:
            message = "From/To date request filter the invoice date not found data or missing/empty tracking id. Please import update and try again"
            if self.cr_type == COGS_CONFLICT_CR_TYPE:
                message = "The request filter not found data. Please check the filter and try again"
            raise InvalidFormatException(
                message=message
            )
        return data

    def validate_request(self):
        kwargs = {
            SHIPPING_INVOICE_CR_TYPE: self.validate_request_by_model_filter,
            SHIPPING_INVOICE_TRANS_CR_TYPE: self.validate_request_by_model_filter,
            ITEMS_CR_TYPE: self.validate_request_by_model_filter,
            TOP_ASINS_CR_TYPE: self.validate_request_by_model_filter,
            ANALYSIS_CR_TYPE: self.validate_request_by_ds_query,
            COGS_CONFLICT_CR_TYPE: self.validate_request_by_model_filter,
        }
        return kwargs[self.cr_type]()

    def get_objects(self, sale_item_ids):
        return True

    @swagger_auto_schema(operation_description="create custom report slug profile for filter data source",
                         request_body=CustomReportSlugCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomReportSerializer})
    def post(self, request, *args, **kwargs):
        user_id = AppContext.instance().user_id
        with transaction.atomic():
            time_now = timezone.now()
            data = self.validate_request()
            data.update({
                'client': str(kwargs['client_id']),
                'user': str(user_id),
                'type': self.cr_type,
                'name': f'{self.cr_type}-{time_now.strftime("%m-%d-%Y")}-{token_hex(6)}'
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


class CustomReportDynamicRetrieveUpdateDestroyView(CustomReportRetrieveUpdateDestroyView):
    pass


class CancelCustomReportDynamicView(CancelCustomReportView):
    pass
