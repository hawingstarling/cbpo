from typing import List

from rest_framework import serializers

from app.payments.models import (
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    Plan,
    Subscription,
    FundPackage,
)
from app.tenancies.models import Client, User


class _LabelServiceKeySerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.ReadOnlyField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        exclude = (
            "is_removed",
            "external_plan_id",
        )


class ServiceConfigKeySerializer(serializers.Serializer):
    tenancy_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), allow_null=True
    )
    plan_service_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), allow_null=True
    )
    daily_limitation_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), allow_null=True
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PlanConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "name",
            "type",
            "price",
            "application",
            "tenancy_config",
        )

    price = serializers.FloatField(read_only=True)
    tenancy_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), source="get_tenancy_config"
    )


class MwPlanConfigSerializer(PlanConfigSerializer):
    plan_service_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), source="get_plan_service_config"
    )
    daily_limitation_config = serializers.ListSerializer(
        child=_LabelServiceKeySerializer(), source="get_daily_limitation_config"
    )

    class Meta(PlanConfigSerializer.Meta):
        fields = PlanConfigSerializer.Meta.fields + (
            "plan_service_config",
            "daily_limitation_config",
        )


class TransitPlanConfigSerializer(PlanConfigSerializer):
    class Meta(PlanConfigSerializer.Meta):
        pass


class PlanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "type",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanTypeSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        exclude = (
            "is_removed",
            "external_subscription_id",
        )


class ApprovalOrganizationalPaymentSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)
    subscription_config = ServiceConfigKeySerializer(
        source="get_config", allow_null=True
    )
    clients = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ApprovalOrganizationalPayment
        exclude = ("is_removed",)

    def get_clients(self, instance):  # noqa

        client_ids = Client.objects.filter(
            organization_id=instance.organization_id
        ).values_list("id", flat=True)
        return client_ids


class _UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalOrganizationalPayment
        exclude = ("is_removed", "organization", "subscription")


class OrganizationSubscriptionConfigSerializer(serializers.ModelSerializer):
    clients = serializers.SerializerMethodField(read_only=True)
    config = ServiceConfigKeySerializer()

    class Meta:
        model = ApprovalOrganizationalServiceConfig
        fields = ("id", "clients", "config")

    @classmethod
    def get_clients(cls, instance) -> List[str]:
        return Client.objects.filter(organization_id=instance.id).values_list(
            "id", flat=True
        )

    def validate(self, attrs):
        return attrs


class UserLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "avatar")


class FundPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundPackage
        exclude = ("is_removed",)
