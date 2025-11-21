import logging
from app.financial.permissions.fedex_shipment_permissions import ViewFedExShipmentPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from app.financial.services.fedex_shipment.utils import get_query_set_filter_shipping_invoice
from app.financial.sub_serializers.shipping_invoice_serializer import ShippingInvoiceSerializer

logger = logging.getLogger(__name__)


class ListShippingInvoiceView(generics.ListAPIView):
    serializer_class = ShippingInvoiceSerializer
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
        #
        status = self.request.query_params.get('status')
        source = self.request.query_params.get('source')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        sort_field = self.request.query_params.get('sort_field')
        if not sort_field:
            sort_field = 'invoice_date'
        sort_direction = self.request.query_params.get('sort_direction')
        if not sort_direction:
            sort_direction = 'desc'
        keyword = self.request.query_params.get('keyword')
        queryset = get_query_set_filter_shipping_invoice(client_id=client_id, from_date=from_date, to_date=to_date,
                                                         status=status, source=source, sort_field=sort_field,
                                                         sort_direction=sort_direction, keyword=keyword)
        return queryset
