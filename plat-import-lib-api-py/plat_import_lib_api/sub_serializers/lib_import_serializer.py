import json
import logging
import os
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from rest_framework.fields import empty

from plat_import_lib_api.static_variable.config import MEDIA_ROOT, BASE_URL, MEDIA_URL
from plat_import_lib_api.static_variable.config import plat_import_setting
from rest_framework import serializers
from ..models import DataImportTemporary, UPLOADING, VALIDATING, PROCESSING, RawDataTemporary
from ..services.controllers.manage import ImportJobManager
from ..services.files.storage import StorageFileManage, STORAGE_UPLOAD_ACTION
from ..services.utils.response import ResponseDataService
from ..services.utils.utils import create_path_file
from ..services.utils.utils import load_lib_module
from ..static_variable.action import UPLOAD_ACTION, VALIDATE_ACTION, PROCESS_ACTION
from ..sub_serializers.common_serializer import ColumnsMappingResponseSerializer, TargetColumnsSerializer

logger = logging.getLogger(__name__)


class LibImportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataImportTemporary
        fields = '__all__'
        extra_fields = {
            'id': {'read_only': True},
            'created': {'read_only': True},
            'modified': {'read_only': True},
        }

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        view = self.context['view']
        self.module = view.kwargs['module']
        self.lib_module = load_lib_module(self.module)

    def to_representation(self, instance):
        instance.refresh_from_db()
        response = ResponseDataService(lib_import_id=str(instance.pk))
        return response.data_import

    def map_info_file(self, file_path: any, module: str, data: dict):
        try:
            storage_service = StorageFileManage(file_path=file_path, module=module, action=STORAGE_UPLOAD_ACTION)
            file_path = storage_service.process()
            logger.info(f"File path info : {file_path}")
            data.update(temp_file_path=file_path)
            if plat_import_setting.storage_location == 'google':
                data.update(file_url_cloud=file_path)
        except Exception as ex:
            logger.error(f'[LibImportModelSerializer][storage_file]: {ex}')
            raise NotImplementedError

    @staticmethod
    def make_temp_file_inmemory(module, file):
        _, ext = os.path.splitext(file.name)
        file_path = create_path_file(file.name, module, "temp")
        default_storage.save(file_path, ContentFile(file.read()))
        return os.path.join(MEDIA_ROOT, file_path)

    def setup_meta_lib_import(self, instance: DataImportTemporary = None):
        meta_init = {}
        if instance:
            meta_init = instance.meta
        meta = self.lib_module.setup_metadata(meta_init, self.context)
        return meta

    def create(self, validation_data):

        # upload file and get info file
        request = self.context.get('request')
        # created record lib import
        module = self.module
        meta = self.setup_meta_lib_import()
        file = request.FILES.get('file')
        # get meta payload 
        try:
            meta_payload = request.data.get('meta', {})
            if meta_payload:
                if isinstance(meta_payload, str):
                    meta_payload = json.loads(meta_payload)
                if isinstance(meta_payload, dict):
                    meta.update(meta_payload)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
        #
        meta['file_name'] = file.name
        client_id = meta.get("client_id", None)

        data = dict(
            client_id=client_id,
            module=module,
            module_label=self.lib_module.__LABEL__,
            meta=meta,
            status=UPLOADING,
            progress=0
        )

        if isinstance(file, InMemoryUploadedFile):
            file_path = self.make_temp_file_inmemory(module, file)
        else:
            file_path = file.file.name
        self.map_info_file(file_path=file_path, data=data, module=module)
        instance = super().create(data)
        return instance

    def do_action_job(self, lib_import_id: str, action: str, map_config_request: list = []):
        job_manage = ImportJobManager(lib_import_id=lib_import_id, action=action, map_config_request=map_config_request)
        job_manage.process()


class ImportHistorySerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(source="get_file")
    username = serializers.SerializerMethodField(source="get_username")
    summary = serializers.SerializerMethodField(source="get_summary")

    class Meta:
        model = DataImportTemporary
        fields = ("id", "module", "module_label", "created", "file", "username", "status", "progress", "summary")

    @classmethod
    def get_file(cls, ins) -> dict:
        url = ins.file_url_cloud
        if not url:
            url = f'{ins.temp_file_path.replace(f"{MEDIA_ROOT}/", f"{BASE_URL}{MEDIA_URL}")}'
        name = ins.meta.get("file_name")
        if not name:
            file_parse = urlparse(url)
            name = os.path.basename(file_parse.path)
        return {
            "name": name,
            "url": url
        }

    @classmethod
    def get_username(cls, ins) -> str:
        # optional from meta field
        return ins.meta.get("username")

    @classmethod
    def get_summary(cls, ins) -> dict:
        return RawDataTemporary.summary(ins.pk)


class UploadDataImportSerializer(LibImportModelSerializer):
    file = serializers.FileField(required=True)
    meta = serializers.JSONField(default={})

    class Meta(LibImportModelSerializer.Meta):
        fields = ['file', 'meta']

    def create(self, validation_data):
        instance = super().create(validation_data)
        self.do_action_job(lib_import_id=str(instance.pk), action=UPLOAD_ACTION)
        return instance


class ValidateDataImportSerializer(LibImportModelSerializer):
    column_mapping = serializers.ListField(allow_empty=False, child=ColumnsMappingResponseSerializer(), write_only=True)

    class Meta(LibImportModelSerializer.Meta):
        fields = ('column_mapping',)

    def update(self, instance, validation_data):
        meta = self.setup_meta_lib_import(instance)
        data = dict(
            status=VALIDATING,
            progress=0,
            meta=meta,
            validation_started=timezone.now(),
            validation_completed=None
        )
        instance = super().update(instance, data)
        map_config_request = validation_data['column_mapping']
        self.do_action_job(lib_import_id=str(instance.pk), action=VALIDATE_ACTION,
                           map_config_request=map_config_request)
        return instance


class ProcessDataImportSerializer(LibImportModelSerializer):

    def update(self, instance, validation_data):
        meta = self.setup_meta_lib_import(instance)
        data = dict(
            status=PROCESSING,
            progress=0,
            meta=meta,
            process_started=timezone.now(),
            process_completed=None
        )
        instance = super().update(instance, data)
        self.do_action_job(lib_import_id=str(instance.pk), action=PROCESS_ACTION)
        return instance


class ItemsDataImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDataTemporary
        fields = '__all__'
        extra_fields = {
            'id': {'read_only': True},
            'created': {'read_only': True},
            'modified': {'read_only': True},
        }

    def to_representation(self, instance):
        _type_request = self.context['request'].query_params.get('type')
        if not _type_request:
            _type_request = 'raw'
        return instance.normalize_raw_response(_type_request)


class ExportSampleSerializer(serializers.Serializer):
    file_uri = serializers.CharField()


class ExportDataImportSerializer(LibImportModelSerializer):
    file_uri = serializers.CharField()

    class Meta(LibImportModelSerializer.Meta):
        fields = ('file_uri',)

    def to_representation(self, instance):
        try:
            instance.refresh_from_db()
            # temp data
            type_filter = self.context.get('type_filter')
            filters = {'type': type_filter}
            # data
            kwargs = self.context['view'].kwargs
            url = self.lib_module.export(lib_import_id=str(instance.pk), filters=filters, **kwargs)
            data = {'file_uri': url}
            return data
        except Exception as ex:
            logger.error(f'[ExportDataImportSerializer]: {ex}')


class ModuleColumnsSerializer(serializers.Serializer):
    name = serializers.CharField()
    label = serializers.CharField()
    columns = serializers.ListField(child=TargetColumnsSerializer())

    class Meta:
        ref_name = 'module_columns'
