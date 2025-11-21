import hashlib
import json
import logging
import copy
import pytz
from django.conf import settings
from django.db.models import CharField
from django.db.models.functions import Cast
from django.utils import timezone
from rest_framework.status import HTTP_200_OK
from app.core.services.tinyurl import TinyURLManager
from app.core.utils import send_twilio_message
from app.financial.models import Alert, AlertItem, SaleItem, CustomObject, AlertDelivery, AlertDigest
from app.financial.services.alert.ref_object_config.ref_object import ref_object_template
from app.financial.services.financial_notification import EmailServices
from app.financial.variable.alert import EMAIL_VARIABLE, SMS_VARIABLE
from app.financial.variable.common import ERROR_STATUS, DONE_STATUS

logger = logging.getLogger(__name__)


class AlertDeliveryChannel:
    def __init__(self, client_id, alert_id):
        self.client_id = client_id
        self.alert_id = alert_id
        self.alert = Alert.objects.tenant_db_for(client_id).get(pk=alert_id)
        self.time_now = timezone.now()
        self.tz = pytz.timezone(settings.DS_TZ_CALCULATE)
        #
        self.alert_digest = self.on_process_alert_digest()
        self.alert_digest_name = None
        #
        self.tinyurl_manage = TinyURLManager(client_id=self.client_id)

    def on_validate(self):
        assert self.alert_digest is not None, "Alert Digest is not empty"
        self.alert_digest_name = self.alert_digest.name
        return self

    def create_tiny_url(self, ref_link: str):
        try:
            payloads = {
                'url': ref_link,
                'domain': 'tinyurl.com'
            }
            rs = self.tinyurl_manage.create_link(payloads)
            status_code = rs.status_code
            content = json.loads(rs.content.decode('utf-8'))
            logger.info(
                f"[{self.__class__.__name__}][{self.client_id}][{self.alert_digest_name}][create_tinyurl] status {status_code} , content {content}")
            if status_code == HTTP_200_OK:
                ref_link = content["data"]["tiny_url"]
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][{self.alert_digest_name}][create_tinyurl] {ex}")
        return ref_link

    def on_process(self):
        #
        queryset = AlertItem.objects.tenant_db_for(self.client_id).filter(client_id=self.client_id,
                                                                          alert_digest=self.alert_digest)
        if not queryset.exists():
            return self
        sale_item_ids = list(
            queryset.annotate(sale_item_id_cast=Cast('sale_item_id', CharField())).values_list('sale_item_id_cast',
                                                                                               flat=True))
        try:
            self.update_alert_digest_info(is_digest=True)
            #
            ref_link_id = self.on_process_ref_link(sale_item_ids)
            ref_link = f"{settings.BASE_HOME_URL}/#/pf/{self.client_id}/analysis?ref={ref_link_id}"
            # create tinyurl
            ref_link = self.create_tiny_url(ref_link)
            #
            if self.alert.users:
                # TODO: handler notification
                pass
            if self.alert.emails:
                self.on_process_alert_channel_emails(sale_item_ids, ref_link)
            if self.alert.phones:
                self.on_process_alert_channel_sms(sale_item_ids, ref_link)
        except Exception as ex:
            self.update_alert_digest_info(is_digest=False)
            logger.error(f"[{self.__class__.__name__}][on_process] {ex}]")

        return self

    def on_complete(self):
        if self.alert.throttling_alert:
            self.alert.last_throttling_period = self.time_now
            self.alert.save()

    def update_alert_digest_info(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self.alert_digest, attr, value)
        self.alert_digest.save()

    def on_process_init_alert_delivery(self, via: str, to: [str]):
        return AlertDelivery.objects.tenant_db_for(self.client_id).get_or_create(client_id=self.client_id,
                                                                                 alert_digest=self.alert_digest,
                                                                                 via=via, defaults=dict(to=to))

    def on_process_alert_channel_emails(self, sale_item_ids, ref_link):
        alert_delivery, _ = self.on_process_init_alert_delivery(via=EMAIL_VARIABLE, to=self.alert.emails)
        if alert_delivery.status == DONE_STATUS:
            return
        status = DONE_STATUS
        logs = []
        try:
            sale_items = SaleItem.objects.tenant_db_for(self.client_id).filter(pk__in=sale_item_ids) \
                .order_by('-sale_date')
            data = []
            for item in sale_items:
                data.append({
                    'channel': item.sale.channel.name,
                    'channel_sale_id': item.sale.channel_sale_id,
                    'sale_date': item.sale_date.astimezone(tz=self.tz).strftime('%m/%d/%Y %H:%M:%S'),
                    'brand': item.brand.name if item.brand is not None else '',
                    'sku': item.sku,
                    'total_charged': item.total_charged,
                    'profit': item.profit,
                    'margin': item.margin,
                })
            #
            email_service = EmailServices()
            email_service.send_sale_alert(team_name='PF', receiver_name='there',
                                          view_name=self.alert.custom_view.name,
                                          ref_link=ref_link, items=data, recipient_list=self.alert.emails)
        except Exception as ex:
            status = ERROR_STATUS
            logs.append(str(ex))
        logs = ", ".join(logs)
        #
        alert_delivery.status = status
        alert_delivery.logs = logs
        alert_delivery.save()

    def on_process_alert_channel_sms(self, sale_item_ids, ref_link):
        alert_delivery, _ = self.on_process_init_alert_delivery(via=SMS_VARIABLE, to=self.alert.phones)
        if alert_delivery.status == DONE_STATUS:
            return
        status = DONE_STATUS
        logs = []
        #
        body = f"""This is an alert for new sale(s) found under your Precise Financial view “{self.alert.custom_view.name}”. Please check via {ref_link}"""
        for phone in self.alert.phones:
            try:
                sms = send_twilio_message(phone, body)
                logger.info(sms.sid)
            except Exception as ex:
                status = ERROR_STATUS
                logs.append(str(ex))
        logs = ", ".join(logs)
        #
        alert_delivery.status = status
        alert_delivery.logs = logs
        alert_delivery.save()

    def on_process_alert_digest(self):
        try:
            return AlertDigest.objects.tenant_db_for(self.client_id).get(client_id=self.client_id,
                                                                         alert_id=self.alert_id, is_digest=False)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][on_process_get_alert_digest] {ex}]")
        return None

    @property
    def get_query_ds(self):
        try:
            return self.alert.custom_view.ds_filter["base"]["config"]["query"]
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_query_ds] {ex}]")
        return {}

    def on_process_ref_link(self, sale_item_ids):
        content = copy.deepcopy(ref_object_template)
        cond_in = {
            "id": None,
            "type": "OR",
            "level": 0,
            "config": {
                "format": {
                    "temporal": {
                        "date": {
                            "type": "date",
                            "formatLabel": "MM/DD/YYYY",
                            "formatValue": "YYYY-MM-DD"
                        },
                        "datetime": {
                            "type": "datetime",
                            "formatLabel": "MM/DD/YYYY hh:mm:ss A",
                            "formatValue": "YYYY-MM-DDTHH:mm:ss"
                        }
                    }
                },
                "ignore": {
                    "base": {
                        "value": True,
                        "visible": True
                    },
                    "global": {
                        "value": False,
                        "visible": False
                    }
                }
            },
            "enabled": True,
            "conditions": [
                {
                    "value": sale_item_ids,
                    "column": {
                        "name": "sale_item_id",
                        "type": "text",
                        "displayName": "Sale Item ID"
                    },
                    "operator": "in",
                    "parentId": None
                }
            ],
            "enabledFilterReadable": False
        }
        #
        query = copy.deepcopy(self.get_query_ds)

        content["q"]["base"]["config"]["query"] = query
        content["q"]["builder"]["config"]["query"] = cond_in
        hash_content = hashlib.md5(json.dumps(content).encode('utf-8')).hexdigest()
        #
        ref, _ = CustomObject.objects.tenant_db_for(self.client_id).get_or_create(client_id=self.client_id,
                                                                                  hash_content=hash_content,
                                                                                  content=content)
        ref_link_id = str(ref.id)
        return ref_link_id
