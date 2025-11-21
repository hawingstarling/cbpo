import logging

from django.db.models import Q
from django.http import Http404
from rest_framework import generics
from app.financial.models import SaleItemTransaction, SaleItem
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.sale_item_trans_event_serializer import SaleItemTransEventSerializer
from app.financial.variable.shipping_cost_source import SHIP_CARRIER_FEDEX, SHIPPING_COST_SOURCE_TRANS_EVENT

logger = logging.getLogger(__name__)


class ClientSaleItemTransEventView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = SaleItemTransEventSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context.update({
                'instance': self.content_object
            })
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.kwargs}][get_serializer_context] {ex}")
        return context

    @property
    def content_object(self):
        try:
            sale_item_id = self.kwargs.get('sale_item_id')
            return SaleItem.objects.tenant_db_for(self.kwargs.get('client_id')).get(pk=sale_item_id)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][{self.kwargs}][content_object] {ex}")
            raise Http404

    def get_queryset(self):

        client_id = self.kwargs.get('client_id')

        column = self.request.query_params.get('column', None)

        event = self.request.query_params.get('event', None)

        try:
            event = event.lower()
        except Exception as ex:
            logger.debug(f"[{self.__class__.__name__}][{self.kwargs}][get_queryset] {ex}")

        #
        content_object = self.content_object

        sale_instance = content_object.sale

        filter_object = {
            'client_id': client_id,
            'channel': sale_instance.channel,
            'channel_sale_id': sale_instance.channel_sale_id,
            'sku': content_object.sku
        }

        kwargs = dict(
            fulfillment_type=content_object.fulfillment_type,
            is_prime=sale_instance.is_prime,
            event=event
        )

        if column:
            columns_filter = SaleItemTransaction().query_lookup_column(column, filter_object, **kwargs)

            if column == 'shipping_cost':
                try:
                    assert content_object.shipping_cost_source in SHIPPING_COST_SOURCE_TRANS_EVENT, \
                        f"The shipping cost source invalid"
                    if content_object.fulfillment_type.name.startswith('MFN') \
                            and content_object.ship_carrier and SHIP_CARRIER_FEDEX in content_object.ship_carrier:
                        columns_filter = Q(pk=None)
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][{self.kwargs}][get_queryset] {ex}")
                    columns_filter = Q(pk=None)
            return SaleItemTransaction.objects.tenant_db_for(client_id).filter(columns_filter)
        return SaleItemTransaction.objects.tenant_db_for(client_id).filter(**filter_object)
