import uuid
from django.db import models
from django.db.models import When, Count, Case, IntegerField
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.contrib.postgres.indexes import GinIndex
from plat_import_lib_api.static_variable.raw_data_import import RAW_TYPE_CONFIG, RAW_CREATED_TYPE, RAW_UPDATED_TYPE, \
    RAW_IGNORED_TYPE, RAW_DELETED_TYPE

UPLOADING = 'uploading'
UPLOADED = 'uploaded'
VALIDATING = 'validating'
VALIDATED = 'validated'
PROCESSING = 'processing'
PROCESSED = 'processed'
FAILURE = 'failure'
REVOKED = 'revoked'
REVERTING = 'reverting'
REVERTED = 'reverted'
REPORTING = 'reporting'
REPORTED = 'reported'

STATUS_CHOICE = (
    (UPLOADING, 'Uploading'),
    (UPLOADED, 'Uploaded'),
    (VALIDATING, 'Validating'),
    (VALIDATED, 'Validated'),
    (PROCESSING, 'Processing'),
    (PROCESSED, 'Processed'),
    (FAILURE, 'Failure'),
    (REVOKED, 'Revoked'),
    (REVERTING, 'Reverting'),
    (REVERTED, 'Reverted'),
    (REPORTING, 'Reporting'),
    (REPORTED, 'Reported'),
)

GOOGLE_TYPE = 'google'
LOCAL_TYPE = 'local'

TEMP_FILE_TYPE = (
    (GOOGLE_TYPE, 'Google Storage'),
    (LOCAL_TYPE, 'Local storage')
)


class DataImportTemporary(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(null=True)
    module = models.CharField(max_length=100)
    module_label = models.CharField(max_length=100, default=None, null=True, blank=True)
    meta = models.JSONField(default=dict)
    meta_hash = models.CharField(max_length=255, default=None, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default=UPLOADING,
                              verbose_name='status of file temp')
    log = models.TextField(verbose_name='log import data file', null=True, default=None)
    progress = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # progress percent of status
    total_process = models.IntegerField(verbose_name='Total process record by status', default=0)
    info_import_file = models.JSONField(default=dict)
    temp_file_path = models.TextField(default=None, null=True)
    file_url_cloud = models.TextField(default=None, null=True)
    temp_file_path_type = models.CharField(max_length=20, choices=TEMP_FILE_TYPE, default=LOCAL_TYPE,
                                           verbose_name='Temp file path type')
    time_exc = models.TextField(default=None, null=True)
    json_data = models.TextField(default='{}', null=True, verbose_name='Json Data Origin')
    json_data_last_cache = models.TextField(default='{}', null=True, verbose_name="Json Data Last Cache")
    validation_started = models.DateTimeField(default=None, null=True)
    validation_completed = models.DateTimeField(default=None, null=True)
    process_started = models.DateTimeField(default=None, null=True)
    process_completed = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.id} - {self.module} - {self.status} - {self.progress}"

    class Meta:
        indexes = [
            models.Index(fields=['module', 'client_id'], name='module_client_id_idx'),
            models.Index(fields=['module', 'client_id', 'meta_hash', 'progress'], name='module_client_id_hash_idx'),
            models.Index(fields=['module', 'status'], name='module_status_idx'),
            GinIndex(name='meta_json_index', fields=['meta'], opclasses=['jsonb_path_ops']),
            GinIndex(name='info_import_file_json_index', fields=['info_import_file'], opclasses=['jsonb_path_ops']),
        ]


class RawDataTemporary(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lib_import = models.ForeignKey(DataImportTemporary, on_delete=models.CASCADE)
    index = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default=UPLOADED)
    data = models.JSONField(default=dict)
    map_config = models.JSONField(default=dict)
    data_map_config = models.JSONField(default=dict)
    type = models.CharField(max_length=50, choices=RAW_TYPE_CONFIG, default=RAW_CREATED_TYPE)
    is_valid = models.BooleanField(default=None, null=True)
    is_complete = models.BooleanField(default=None, null=True)
    validation_errors = models.JSONField(default=list)
    processing_errors = models.JSONField(default=list)
    key_map = models.TextField(default=None, null=True, verbose_name='Key mapping config')
    parent_key_map = models.TextField(default=None, null=True, verbose_name='Parent key mapping config')
    meta_addition = models.JSONField(default=dict)
    hash_data = models.CharField(max_length=32)  # md5

    def __str__(self):
        return f"{self.lib_import} - {self.index} - {self.status}"

    class Meta:
        unique_together = ['lib_import', 'hash_data']
        indexes = [
            models.Index(fields=['lib_import', 'status']),
            models.Index(fields=['lib_import', 'hash_data']),
            models.Index(fields=['lib_import', 'key_map']),
            models.Index(fields=['lib_import', 'parent_key_map']),
            GinIndex(name='data_json_index', fields=['data'], opclasses=['jsonb_path_ops']),
            GinIndex(name='data_map_config_json_index', fields=['data_map_config'], opclasses=['jsonb_path_ops']),
        ]

    def normalize_raw_response(self, type_request):
        try:
            if type_request == 'raw':
                data = self.data
            else:
                data = self.data_map_config
            data.update(dict(_meta=self.meta))
            return data
        except Exception as ex:
            return {}

    @property
    def meta(self):
        return {
            'number': self.index,
            'valid': self.is_valid,
            'type': self.type,
            'complete': self.is_complete,
            'validation_errors': self.validation_errors,
            'processing_errors': self.processing_errors,
            **self.meta_addition
        }

    @staticmethod
    def summary(lib_import_id):
        fields = ["total", "valid", "completed", "created", "updated", "ignored", "deleted"]
        try:
            agg = RawDataTemporary.objects.filter(lib_import_id=lib_import_id).aggregate(
                total=Count('id'),
                valid=Count(Case(
                    When(is_valid=True, then=1),
                    output_field=IntegerField(),
                )),
                completed=Count(Case(
                    When(status__in=[PROCESSED, REVERTED, REPORTED], is_complete=True, then=1),
                    output_field=IntegerField(),
                )),
                created=Count(Case(
                    When(status__in=[PROCESSED, REVERTED, REPORTED], is_complete=True, type=RAW_CREATED_TYPE, then=1),
                    output_field=IntegerField(),
                )),
                updated=Count(Case(
                    When(status__in=[PROCESSED, REVERTED, REPORTED], is_complete=True, type=RAW_UPDATED_TYPE, then=1),
                    output_field=IntegerField(),
                )),
                ignored=Count(Case(
                    When(status__in=[PROCESSED, REVERTED, REPORTED], is_complete=True, type=RAW_IGNORED_TYPE, then=1),
                    output_field=IntegerField(),
                )),
                deleted=Count(Case(
                    When(status__in=[PROCESSED, REVERTED, REPORTED], is_complete=True, type=RAW_DELETED_TYPE, then=1),
                    output_field=IntegerField(),
                )),
            )
            return {ele: agg[ele] for ele in fields}
        except Exception as ex:
            print(ex)
            return {ele: 0 for ele in fields}


class AsinTest(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_id = models.CharField(max_length=100, verbose_name="Profile Id")
    brand = models.CharField(max_length=100, verbose_name="Brand")
    upc = models.FloatField(verbose_name="Upc")
    asin = models.CharField(max_length=100, verbose_name="Asin")
    sku = models.CharField(max_length=100, verbose_name="Sku")
    domain = models.CharField(max_length=100, verbose_name="Domain")
    frequency = models.CharField(max_length=100, verbose_name="Frequency")
    cost = models.FloatField(verbose_name="Cost")
    posted_date = models.DateTimeField(blank=True, null=True, verbose_name="Posted Date")

    class Meta:
        unique_together = ('profile_id', 'brand', 'asin')


class Health(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=50, null=False, unique=True)
    is_enabled = models.BooleanField(default=True)
    is_healthy = models.BooleanField(default=True)
    message = models.TextField()
    client_ids = PostgresArrayField(models.UUIDField(unique=True, max_length=32), default=list, blank=True)
    import_ids = PostgresArrayField(models.UUIDField(unique=True, max_length=32), default=list, blank=True)

    def __str__(self):
        return f"{self.module_name} - {self.is_enabled} - {self.is_healthy}"


class Setting(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_queue = models.BooleanField(default=False)
    bulk_process_size = models.IntegerField(default=2000)
    storage_location = models.CharField(max_length=100, default='local')
    storage_folder = models.CharField(max_length=100, default='plat/lib_imports')
    round_up_currency = models.DecimalField(decimal_places=2, max_digits=6, default=0.0)
    google_cloud_storage_bucket_name = models.CharField(max_length=200, default=None, null=True)
    google_cloud_storage_bucket_access_key = models.CharField(max_length=200, default=None, null=True)
    date_time_format = models.CharField(max_length=100, default='%Y-%m-%d %H:%M:%S')
    module_template_location = models.CharField(max_length=200, default='plat_import_lib_api.services.modules.base')
    healthy_check_minute = models.IntegerField(default=30)
    auto_clean_day = models.IntegerField(default=30)
    module_reopen_exclude = PostgresArrayField(models.CharField(unique=True, max_length=100), default=list, blank=True)
