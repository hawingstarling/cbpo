import copy
import logging

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.financial.models import Channel
from app.financial.sub_serializers.organization_serializer import ClientSerializer
from app.database.sub_serializers.tenant_db_for_serializer import TenantDBForSerializer
from app.financial.sub_serializers.user_serializer import UserSerializer
from app.financial.variable.activity_variable import REVOKED_SP_REPORT_KEY
from app.job.utils.helper import register
from app.job.utils.variable import MODE_RUN_IMMEDIATELY, SELLING_PARTNER_CATEGORY, COMMUNITY_CATEGORY
from app.selling_partner.models import SPReportCategory, SPReportType, SPReportClient
from app.selling_partner.variables.report_source import SPAPI_SOURCE_TYPE
from app.selling_partner.variables.report_status import CANCELLED_STATUS, IN_PROGRESS_STATUS, READY_STATUS

logger = logging.getLogger(__name__)


class SPReportTypeSerializer(TenantDBForSerializer):
    class Meta:
        model = SPReportType
        fields = '__all__'


class SPReportCategoriesSerializer(TenantDBForSerializer):
    report_types = SPReportTypeSerializer(many=True, read_only=True)

    class Meta:
        model = SPReportCategory
        fields = '__all__'

    def to_representation(self, obj):
        self.fields['sub_categories'] = SPReportCategoriesSerializer(many=True, read_only=True)
        return super().to_representation(obj)


class SPReportClientSerializer(TenantDBForSerializer):
    channel = serializers.CharField(max_length=255, default="amazon.com", required=False, allow_blank=True)

    class Meta:
        model = SPReportClient
        fields = '__all__'

    def validate_channel(self, val):
        if not val:
            val = "amazon.com"
        errors = []
        # find brand in system
        try:
            val = Channel.objects.tenant_db_for(self.client_id).get(name=val)
        except Channel.DoesNotExist:
            errors.append('"{}" channel does not exist'.format(val))
        if errors:
            raise ValidationError(errors, code="channel")
        return val

    def validate(self, attrs):
        errors = []
        report_type = attrs["report_type"]
        if report_type.value not in ["GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2"]:
            if not attrs.get("date_range_covered_start"):
                errors.append("Covered start date cannot be null")
            if not attrs.get("date_range_covered_end"):
                errors.append("Covered end date cannot be null")
        else:
            attrs.update(dict(date_range_covered_start=None, date_range_covered_end=None))
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        try:
            #
            validated_data_cp = copy.deepcopy(validated_data)
            obj = self.Meta.model.objects.tenant_db_for(self.client_id) \
                .get(client=validated_data_cp.pop("client"),
                     channel=validated_data_cp.pop("channel"),
                     date_range_covered_start=validated_data_cp.pop("date_range_covered_start"),
                     date_range_covered_end=validated_data_cp.pop("date_range_covered_end"),
                     report_type=validated_data_cp.get("report_type"))
            status_verifying = [IN_PROGRESS_STATUS, READY_STATUS] if obj.report_type.source == SPAPI_SOURCE_TYPE \
                else [IN_PROGRESS_STATUS]
            assert obj.status not in status_verifying
            for k, v in validated_data_cp.items():
                setattr(obj, k, v)
            obj.save()
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            obj = super().create(validated_data)
        transaction.on_commit(lambda: self.register(obj))
        return obj

    def register(self, obj: SPReportClient):
        if obj.report_type.source == SPAPI_SOURCE_TYPE:
            if obj.ac_report_id is None:
                data = dict(
                    name=f"register_sp_report_of_client_{obj.pk}",
                    job_name="app.selling_partner.jobs.report.register_sp_report_of_client",
                    module="app.selling_partner.jobs.report",
                    method="register_sp_report_of_client",
                    meta=dict(client_id=self.client_id, sp_report_id=obj.pk)
                )
                register(category=SELLING_PARTNER_CATEGORY, client_id=self.client_id, **data,
                         mode_run=MODE_RUN_IMMEDIATELY)
        else:
            if obj.report_type.value == "BRANDS_SUMMARY_MONTHLY_DATA_REPORT":
                data = dict(
                    name=f"handler_generate_sp_report_brands_summary_workspace_{self.client_id}",
                    job_name="app.selling_partner.jobs.report_brand_summary."
                             "handler_generate_sp_report_brands_summary_workspace",
                    module="app.selling_partner.jobs.report_brand_summary",
                    method="handler_generate_sp_report_brands_summary_workspace",
                    meta=dict(client_id=self.client_id, sp_report_client_id=obj.pk)
                )
                register(category=SELLING_PARTNER_CATEGORY, client_id=self.client_id, **data,
                         mode_run=MODE_RUN_IMMEDIATELY)

    def to_representation(self, obj):
        self.fields['report_type'] = SPReportTypeSerializer()
        self.fields['creator'] = UserSerializer()
        return super().to_representation(obj)

    def revoke(self, obj: SPReportClient):
        obj.status = CANCELLED_STATUS
        obj.msg_error = {"code": "Cancelled", "message": "The report was revoke by the user."}
        obj.save()

        rp_id = obj.pk
        client_id = str(obj.client_id)

        # write activity
        data = dict(
            name=f"create_activity_by_action_{client_id}_{rp_id}",
            job_name="app.financial.jobs.activity.create_activity_by_action",
            module="app.financial.jobs.activity",
            method="create_activity_by_action",
            meta=dict(
                client_id=client_id,
                user_id=self.user_request_id,
                action=REVOKED_SP_REPORT_KEY,
                data=dict(
                    sp_report_id=rp_id,
                    batch_ids=obj.batch_ids,
                    date_range_covered=[obj.date_range_covered_start.strftime('%Y-%m-%d'),
                                        obj.date_range_covered_end.strftime('%Y-%m-%d')],
                )
            )
        )
        register(category=COMMUNITY_CATEGORY, client_id=client_id, **data, mode_run=MODE_RUN_IMMEDIATELY)
        if obj.report_type.source == SPAPI_SOURCE_TYPE:
            # register job revoke to AC service
            data = dict(
                name=f"revoke_sp_report_of_client_{rp_id}",
                job_name="app.selling_partner.jobs.report.revoke_sp_report_of_client",
                module="app.selling_partner.jobs.report",
                method="revoke_sp_report_of_client",
                meta=dict(client_id=client_id, sp_report_id=rp_id)
            )
            register(category=SELLING_PARTNER_CATEGORY, client_id=client_id, **data, mode_run=MODE_RUN_IMMEDIATELY)


class SPReportClientGenerateSerializer(SPReportClientSerializer):
    class Meta(SPReportClientSerializer.Meta):
        fields = ['channel', 'report_type', 'date_range_covered_start', 'date_range_covered_end']
        validators = []


class StatSPReportClientSerializer(SPReportClientSerializer):
    client = ClientSerializer(read_only=True)
