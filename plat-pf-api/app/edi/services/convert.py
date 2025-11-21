import logging
import math
import os
from django.conf import settings
from django.core.files.storage import default_storage
import pandas as pd
from app.edi import pythonedi
from app.financial.services.fedex_shipment.config import FEDEX_EDI_SERVICE_TYPE_MAPPING, FEDEX_SHIPMENT_SOURCE_FTP_EDI
from plat_import_lib_api.static_variable.config import plat_import_setting

logger = logging.getLogger(__name__)


class EDIConvertFile:

    def __init__(self):
        self._file_storage = None
        self._source = None
        #
        self.parser = pythonedi.EDIParser(edi_format="810", element_delimiter="*")
        #
        EDIConvertFile.__instance = self

    @property
    def file_storage(self):
        return self._file_storage

    @file_storage.setter
    def file_storage(self, value):
        self._file_storage = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    def processing(self):
        if self.source == FEDEX_SHIPMENT_SOURCE_FTP_EDI:
            return self.processing_ftp_edi()
        else:
            return self.processing_ftp_csv()

    def processing_ftp_csv(self):
        data = []
        errors = []
        if not self.file_storage:
            return data, errors
        path_storage = os.path.join(settings.MEDIA_ROOT, self.file_storage)
        path_storage = default_storage.generate_filename(path_storage)
        # print(f"path_storage = {path_storage}")
        if not default_storage.exists(path_storage):
            # default_storage.delete(path_storage)
            return data, errors
        column_mapping = {
            'shipment_date': 'Ship Date',
            'net_charge_amount': 'Net Chrg',
            'recipient_name': 'Recipient Name',
            'recipient_address_line_1': 'Recipient Address 1',
            'recipient_address_line_2': 'Recipient Address 2',
            'recipient_city': 'Recipient City',
            'recipient_state': 'ST2',
            'recipient_zip_code': 'Postal2',
            'recipient_country': 'Cntry2',
            # Original
            'orig_recipient_name': 'Orig Recip Name',
            'orig_recipient_address_line_1': 'Orig Recip Adr 1',
            'orig_recipient_address_line_2': 'Orig Recip Adr 1',
            'orig_recipient_city': 'Original City',
            'orig_recipient_state': 'ST3',
            'orig_recipient_zip_code': 'Postal3',
            'orig_recipient_country': 'Cntry3',
            # service type
            'service_type': 'Co.Cd'
        }
        columns_file = list(column_mapping.values())
        #
        for segment in pd.read_csv(path_storage, chunksize=plat_import_setting.bulk_process_size, dtype=str):
            logger.info(f"[processing_ftp_csv] processing read segment length : {len(segment)}")
            for index, row in segment.iterrows():
                try:
                    for column in columns_file:
                        if isinstance(row.get(column), float) and math.isnan(row.get(column)):
                            row[column] = None
                    empty = not any(row.get(column) for column in columns_file)
                    if empty:
                        continue
                    convert_data = self.make_data_fedex_shipment_ftp_csv(row, column_mapping)
                    if convert_data:
                        data.append(convert_data)
                except Exception as ex:
                    errors.append({index: str(ex)})
        return data, errors

    def make_data_fedex_shipment_ftp_csv(self, row: dict, column_mapping: dict):
        data = {}
        for field, mapping in column_mapping.items():
            val = row.get(mapping)
            if not val:
                continue
            data.update({field: val})
        return data

    def processing_ftp_edi(self):
        data = []
        errors = []
        if not self.file_storage:
            return data, errors
        path_storage = os.path.join(settings.MEDIA_ROOT, self.file_storage)
        path_storage = default_storage.generate_filename(path_storage)
        # print(f"path_storage = {path_storage}")
        if not default_storage.exists(path_storage):
            # default_storage.delete(path_storage)
            return data, errors
        with open(path_storage, "r") as file:
            test_edi = file.read()
            found_segments, edi_data = self.parser.parse(test_edi)
            # print("\n\n{}".format(found_segments))
            # print("\n\n")
            if len(edi_data) > 0:
                for edi in edi_data:
                    convert_data = self.make_data_fedex_shipment_ftp_edi(edi)
                    if convert_data:
                        data.append(convert_data)
        return data, errors

    def make_data_fedex_shipment_ftp_edi(self, edi_data: dict):
        _data = {}
        _shipment_date = self.get_shipment_date(edi_data)
        _net_charge_amount = self.get_net_charge_amount(edi_data)
        _recipient_information = self.get_recipient_information(edi_data)
        _service_type = self.get_service_type(edi_data)
        if not _shipment_date or _net_charge_amount is None or not _recipient_information.get('recipient_zip_code'):
            logger.error(
                f"[make_data_fedex_shipment_ftp_edi]: data error _shipment_date={_shipment_date}, _net_charge_amount={_net_charge_amount}, _recipient_information={_recipient_information} ")
            return _data
        return dict(
            shipment_date=_shipment_date.date().strftime('%Y%m%s'),
            net_charge_amount=_net_charge_amount,
            recipient_zip_code=self.strip_value(_recipient_information.get('recipient_zip_code')),
            recipient_country=self.strip_value(_recipient_information.get('recipient_country')),
            recipient_state=self.strip_value(_recipient_information.get('recipient_state')),
            recipient_city=self.strip_value(_recipient_information.get('recipient_city')),
            recipient_name=self.strip_value(_recipient_information.get('recipient_name')),
            recipient_address_line_1=self.strip_value(_recipient_information.get('recipient_address_line_1')),
            recipient_address_line_2=self.strip_value(_recipient_information.get('recipient_address_line_2')),
            service_type=self.strip_value(_service_type)
        )

    def get_shipment_date(self, edi_data):
        rs = None
        try:
            _data = edi_data['DTM']
            for item in _data:
                if item['DTM01'] == '035':
                    rs = item['DTM02']
                    break
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_shipment_date] {ex}")
        return rs

    def get_net_charge_amount(self, edi_data):
        rs = None
        try:
            _data = edi_data['L_SAC']
            for item in _data:
                if 'SAC' in item:
                    rs = item['SAC']['SAC05']
                    break
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_net_charge_amount] {ex}")
        return rs

    def get_recipient_information(self, edi_data):
        rs = {}
        try:
            _data = edi_data['L_N1']
            if len(_data) == 0:
                return {}
            item = _data[0]
            if 'N1' in item:
                _rs = self.get_recipient_name(item['N1'])
                rs.update(_rs)
            # if 'N2' in item:
            #   addition info name
            #     _data_n2 = item['N2'][0]
            #     _rs = self.get_address_information(_data_n2)
            if 'N3' in item:
                _data_n3 = item['N3'][0]
                _rs = self.get_address_information(_data_n3)
                rs.update(_rs)
            if 'N4' in item:
                _rs = self.get_geographic_location(item['N4'])
                rs.update(_rs)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][get_recipient_information] {ex}")
        return rs

    def get_recipient_name(self, _data):
        return dict(
            recipient_name=_data.get('N102', None)
        )

    def get_address_information(self, _data):
        return dict(
            recipient_address_line_1=_data.get('N301', None),
            recipient_address_line_2=_data.get('N302', None)
        )

    def get_geographic_location(self, _data):
        return dict(
            recipient_city=_data.get('N401', None),
            recipient_state=_data.get('N402', None),
            recipient_zip_code=_data.get('N403', None),
            recipient_country=_data.get('N404', None)
        )

    def get_service_type(self, _data):
        try:
            value = _data['L_IT1'][0]['IT1']['IT111']
            return FEDEX_EDI_SERVICE_TYPE_MAPPING[int(value)]
        except Exception as ex:
            # print(ex)
            return None

    def strip_value(self, value):
        if value is None or not isinstance(value, str):
            return value
        value = value.strip()
        if value[-1] == '.':
            value = value[:-1]
        return value
