import logging
import os
from datetime import timedelta
from typing import Union

from django.core.files.storage import default_storage
from django.utils import timezone
from django.conf import settings
from app.edi.models import EdiInvoiceSource
from app.edi.sources.ftp import FTPConnect
from app.financial.models import ClientPortal

logger = logging.getLogger(__name__)

EDI_FEDEX_CLEAN_NUMBER_DAYS = 60


class EDISourceManage:
    def __init__(self, client: ClientPortal, source: Union[FTPConnect]):
        self.client = client
        self.client_id = str(self.client.pk)
        #
        self._source_connect = source

        self.date_now = timezone.now()

        self.edi_invoice = []

    @property
    def source_connect(self):
        return self._source_connect

    @source_connect.setter
    def source_connect(self, value):
        self._source_connect = value

    def archive(self, edi_invoices: [EdiInvoiceSource]):
        logger.info(f"[archive] source name: {self._source_connect.__class__.__name__}")
        #
        file_names = []
        for edi_invoice in edi_invoices:
            file_name = edi_invoice.file_path.split('/')[-1]
            file_names.append(file_name)
        #
        self._source_connect.move_files_edi(directory_origin=f'{settings.FTP_FEDEX_DIR_PREFIX}/in',
                                            directory_target=f'{settings.FTP_FEDEX_DIR_PREFIX}/in-arc',
                                            file_names=file_names)

    def processing(self):
        logger.info(f"[processing] source name: {self._source_connect.__class__.__name__}")
        file_sources = self._source_connect.download_files_edi(directory=f'{settings.FTP_FEDEX_DIR_PREFIX}/in')

        for source in file_sources.keys():
            file_paths = file_sources[source]
            if len(file_paths) == 0:
                continue
            edi_invoices_exist = list(
                EdiInvoiceSource.objects.tenant_db_for(self.client_id).filter(client=self.client, source=source,
                                                                               date=self.date_now.date(),
                                                                               file_path__in=file_paths).values_list(
                    'file_path', flat=True))
            for file_path in file_paths:
                if file_path not in edi_invoices_exist:
                    obj = EdiInvoiceSource(client=self.client, source=source, file_path=file_path)
                    self.edi_invoice.append(obj)
        #
        if self.edi_invoice:
            EdiInvoiceSource.objects.tenant_db_for(self.client_id).bulk_create(self.edi_invoice, ignore_conflicts=True)
            self.edi_invoice = []

    @staticmethod
    def clean_source(client_id: str):
        queryset = EdiInvoiceSource.objects.tenant_db_for(client_id) \
            .filter(client_id=client_id, date__lte=timezone.now().date() - timedelta(days=EDI_FEDEX_CLEAN_NUMBER_DAYS))
        logger.info(f"[{client_id}][clean_source]: query = {queryset.query}")
        path_storages = queryset.values_list('file_path', flat=True).distinct()
        #
        for path_storage in path_storages:
            #
            path_storage = os.path.join(settings.MEDIA_ROOT, path_storage)
            path_storage = default_storage.generate_filename(path_storage)
            if not default_storage.exists(path_storage):
                continue
            default_storage.delete(path_storage)
        #
        queryset.delete()
