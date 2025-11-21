import logging

from django.core.management.base import BaseCommand

from app.financial.models import FulfillmentChannel
from app.financial.variable.fulfillment_channel import FulfillmentChannelEnum

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "This command using for init fulfillment channel."

    def handle(self, *args, **options):
        try:
            logger.info("Start init fulfillment channel")
            fulfillment_channels = []
            for item in FulfillmentChannelEnum:
                fulfillment_channels.append(FulfillmentChannel(name=item.value))
            FulfillmentChannel.objects.bulk_create(objs=fulfillment_channels, ignore_conflicts=True)
            logger.info("End init fulfillment channel")
        except Exception as ex:
            logger.error(f"Command init fulfillment channel errors : {ex}")
