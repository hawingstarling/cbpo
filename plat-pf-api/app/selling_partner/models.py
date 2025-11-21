import uuid
from django.db import models
from django.db.models import Q
from django_better_admin_arrayfield.models.fields import ArrayField
from model_utils.models import TimeStampedModel
from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal, User, Channel
from app.selling_partner.variables.report_source import REPORT_SOURCE_CHOICES, SPAPI_SOURCE_TYPE
from app.selling_partner.variables.report_status import REPORT_STATUS_CHOICE, IN_PROGRESS_STATUS, READY_STATUS


class Setting(TimeStampedModel):
    aws_oauth_consent_url = models.CharField(max_length=255, null=True, blank=True, default=None)
    aws_oauth_access_token_url = models.CharField(max_length=255, null=True, blank=True, default=None)
    aws_oauth_refresh_token_url = models.CharField(max_length=255, null=True, blank=True, default=None)
    web_aws_oauth_redirect = models.CharField(max_length=255, null=True, blank=True, default=None)
    api_aws_oauth_redirect = models.CharField(max_length=255, null=True, blank=True, default=None)
    max_report_retry = models.IntegerField(default=5)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.aws_oauth_consent_url}"


class AppSetting(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE)
    spapi_app_id = models.CharField(max_length=255, null=False, unique=True)
    aws_access_key_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    aws_secret_access_key = models.CharField(max_length=255, null=True, blank=True, default=None)
    aws_default_region = models.CharField(max_length=255, null=False)
    aws_role_arn = models.CharField(max_length=255, null=False)
    amz_lwa_client_id = models.CharField(max_length=255, null=False)
    amz_lwa_client_secret = models.CharField(max_length=255, null=False)
    amz_lwa_expired = models.DateTimeField(null=True, blank=True, default=None)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.spapi_app_id}"


class OauthTokenRequest(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=250)
    spapi_oauth_code = models.CharField(max_length=250)
    selling_partner_id = models.CharField(max_length=250)
    status_code = models.IntegerField(default=400)
    payload = models.JSONField(default=dict)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.selling_partner_id} - {self.spapi_oauth_code} - {self.state}"

    class Meta:
        unique_together = ['state', 'spapi_oauth_code', 'selling_partner_id']
        indexes = [
            models.Index(fields=['selling_partner_id', 'spapi_oauth_code', 'state'])
        ]


class SPOauthClientRegister(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    app_setting = models.ForeignKey(AppSetting, on_delete=models.CASCADE, default=None, null=True, blank=True)
    oauth_token_request = models.ForeignKey(OauthTokenRequest, on_delete=models.CASCADE)
    latest = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.oauth_token_request} - {self.latest}"

    class Meta:
        unique_together = ['client', 'oauth_token_request']
        indexes = [
            models.Index(fields=['client', 'oauth_token_request'])
        ]


class SPReportCategory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', null=True, related_name='sub_categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True)
    sort = models.IntegerField(default=0)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.id} - {self.name} - {self.sort}"

    class Meta:
        unique_together = ['parent', 'value']


class SPReportType(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(SPReportCategory, related_name='report_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    note = models.TextField(null=True)
    is_date_range = models.BooleanField(default=True)
    meta = models.JSONField(default=dict)
    source = models.CharField(max_length=255, choices=REPORT_SOURCE_CHOICES, default=SPAPI_SOURCE_TYPE)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.category} - {self.name} - {self.value}"

    class Meta:
        ordering = ['sort']
        unique_together = ['category', 'name', 'value']


class SPReportClient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    report_type = models.ForeignKey(SPReportType, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, blank=True)
    ac_report_id = models.CharField(max_length=255, default=None, null=True, blank=True)
    batch_ids = ArrayField(models.CharField(unique=True, max_length=255), default=list, blank=True)
    date_range_covered_start = models.DateField(default=None, null=True, blank=True)
    date_range_covered_end = models.DateField(default=None, null=True, blank=True)
    date_requested = models.DateTimeField(default=None, null=True, blank=True)
    date_completed = models.DateTimeField(default=None, null=True, blank=True)
    status = models.CharField(max_length=255, choices=REPORT_STATUS_CHOICE, default=IN_PROGRESS_STATUS)
    file_names = ArrayField(models.CharField(unique=True, max_length=500), default=list, blank=True)
    download_urls = ArrayField(models.CharField(unique=True, max_length=500), default=list, blank=True)
    log = models.TextField(default=None, null=True, blank=True)
    msg_error = models.JSONField(default=dict)
    retry = models.IntegerField(default=0)
    meta = models.JSONField(default=dict)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.report_type} - {self.ac_report_id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'channel', 'report_type', 'date_range_covered_start', 'date_range_covered_end'],
                condition=Q(
                    date_range_covered_start__isnull=False,
                    date_range_covered_end__isnull=False,
                    status__in=[IN_PROGRESS_STATUS, READY_STATUS]
                ),
                name='unique_date_range_covered_is_not_null'),
            models.UniqueConstraint(
                fields=['client', 'channel', 'report_type'],
                condition=Q(
                    date_range_covered_start__isnull=True,
                    date_range_covered_end__isnull=True,
                    status__in=[IN_PROGRESS_STATUS]
                ),
                name='unique_date_range_covered_is_null')
        ]
        indexes = [
            models.Index(fields=['client', 'channel', 'report_type', 'status']),
            models.Index(
                fields=['client', 'channel', 'report_type', 'date_range_covered_start', 'date_range_covered_end']),
            models.Index(fields=['client', 'channel', 'report_type', 'date_requested']),
            models.Index(fields=['client', 'channel', 'report_type', 'date_completed']),
            models.Index(fields=['client', 'channel', 'report_type', 'creator'])
        ]
