import copy
import json
import logging
import os
import uuid

from dictdiffer import diff
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from django.forms import model_to_dict
from django.utils import timezone

from app.edi.configs.status import EDI_INVOICE_PENDING, EDI_INVOICE_DONE, EDI_INVOICE_ERROR, EDI_INVOICE_PROCESS
from app.edi.models import EdiInvoiceSource
from app.edi.services.convert import EDIConvertFile
from app.edi.services.fetch_source import EDISourceManage
from app.edi.sources.ftp import FTPConnect
from app.financial.models import FedExShipment, ClientPortal
from app.financial.sub_serializers.fedex_shipment_serializer import FedEdShipmentFTPSerializer

logger = logging.getLogger(__name__)


class FedExEDIIntegration:

    def __init__(self, client: ClientPortal):
        self.client = client
        self.client_id = str(self.client.pk)
        #
        self.date_now = timezone.now()
        #
        self.edi_convert = EDIConvertFile()

        self.edi_source_manage = EDISourceManage(client=self.client, source=FTPConnect())

        self.fedex_shipment_updated_fields = [i.name for i in FedExShipment._meta.fields if
                                              i.name not in ['pk', 'id', 'shipping_date', 'net_charge_amount',
                                                             'recipient_zip_code']]

    @property
    def condition(self):
        return Q(status=EDI_INVOICE_PENDING, created__lte=self.date_now)

    def get_edi_pending(self):
        queryset = EdiInvoiceSource.objects.tenant_db_for(self.client_id).filter(self.condition)
        return list(queryset)

    def make_edi_process(self):
        EdiInvoiceSource.objects.tenant_db_for(self.client_id).filter(self.condition).update(
            status=EDI_INVOICE_PROCESS, modified=self.date_now)

    def make_edi_complete(self, objs):
        EdiInvoiceSource.objects.tenant_db_for(self.client_id).bulk_update(objs, fields=['status', 'modified', 'log'])

    def is_fedex_changed(self, origin, target):
        _origin = model_to_dict(origin, fields=self.fedex_shipment_updated_fields)
        _target = model_to_dict(target, fields=self.fedex_shipment_updated_fields)
        if len(list(diff(_origin, _target))) > 0:
            return True
        return False

    @staticmethod
    def file_path_ready(file_path):
        path_storage = os.path.join(settings.MEDIA_ROOT, file_path)
        path_storage = default_storage.generate_filename(path_storage)
        if not default_storage.exists(path_storage):
            return False
        return True

    def processing(self):
        fedex_shipment_insert = []
        fedex_shipment_update = []

        edi_invoices = self.get_edi_pending()
        edi_invoices_complete = []

        for edi in edi_invoices:
            if not self.file_path_ready(edi.file_path):
                edi.status = EDI_INVOICE_PENDING
                continue
            log = {}
            self.edi_convert.file_storage = edi.file_path
            self.edi_convert.source = edi.source
            #
            data, data_errors = self.edi_convert.processing()
            self.make_edi_process()

            if not data:
                edi.status = EDI_INVOICE_ERROR
                edi.modified = self.date_now
                edi.log = json.dumps({"errors": data_errors})
                continue
            log.update({'total_records': len(data)})
            #
            number_fedex_error_unique = 0
            number_fedex_same_data = 0
            for index, item in enumerate(data):
                serializer = FedEdShipmentFTPSerializer(data=item)
                serializer.is_valid()
                errors = serializer.errors
                if errors:
                    try:
                        log['errors'].append({index: errors})
                    except Exception as ex:
                        log.update({'errors': [{index: errors}]})
                    continue
                validated_data = serializer.validated_data
                unique_filter = Q(client=self.client,
                                  shipment_date=validated_data.get('shipment_date'),
                                  recipient_name=validated_data.get('recipient_name'),
                                  recipient_zip_code=validated_data.get('recipient_zip_code')
                                  )
                extra_filter = Q(source=self.edi_convert.source,
                                 net_charge_amount=validated_data.get('net_charge_amount'),
                                 recipient_address_line_1=validated_data.get('recipient_address_line_1'))
                queryset = FedExShipment.objects.tenant_db_for(self.client_id).filter(unique_filter)
                find = queryset.filter(extra_filter)
                if find.count() > 0:
                    origin = find.first()
                    target = copy.deepcopy(origin)
                    #
                    for key, val in validated_data.items():
                        if getattr(target, key) != val:
                            setattr(target, key, val)
                    if self.is_fedex_changed(origin, target):
                        fedex_shipment_update.append(target)
                    else:
                        number_fedex_same_data += 1
                    continue
                elif queryset.count() > 0:
                    number_fedex_error_unique += 1
                else:
                    init_data = dict(
                        id=uuid.uuid4(),
                        client=self.client,
                        source=self.edi_convert.source,
                        **validated_data
                    )
                    obj = FedExShipment(**init_data)
                    fedex_shipment_insert.append(obj)
            number_fedex_insert = len(fedex_shipment_insert)
            number_fedex_update = len(fedex_shipment_update)
            if number_fedex_insert > 0:
                FedExShipment.objects.tenant_db_for(self.client_id).bulk_create(fedex_shipment_insert, ignore_conflicts=True)
            if number_fedex_update > 0:
                FedExShipment.objects.tenant_db_for(self.client_id).bulk_update(fedex_shipment_update, fields=self.fedex_shipment_updated_fields)
            edi.status = EDI_INVOICE_DONE
            # add to edi completed if edi done status
            edi_invoices_complete.append(edi)
            #
            log.update({"number_fedex_insert": number_fedex_insert, "number_fedex_update": number_fedex_update,
                        "number_fedex_same_data": number_fedex_same_data,
                        "number_fedex_error_unique": number_fedex_error_unique})
            log = json.dumps(log)
            edi.modified = self.date_now
            edi.log = log
        if len(edi_invoices) > 0:
            self.make_edi_complete(edi_invoices)

        # make archive
        self.edi_source_manage.archive(edi_invoices_complete)
