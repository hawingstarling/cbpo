import uuid
from typing import List, Union

from adminsortable.models import Sortable
from auditlog.registry import auditlog
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Max
from django_better_admin_arrayfield.models.fields import ArrayField
from model_utils.models import SoftDeletableModel, TimeStampedModel

from app.payments.config import (
    APPLICATION_FOR_STRIPE,
    PERIOD_FOR_STRIPE_CHARGING,
    PLAN_TYPE,
    SUBSCRIPTION_ACTIVITY,
    SUBSCRIPTION_MODE,
    PLAN_CUSTOM_ON_DEMAND,
    APP_MWRW,
    APP_TRANSIT,
    COUPON_DURATION_MODE,
)
from app.payments.utils import parse_key_value_label
from app.tenancies.models import Organization, User


# Create your models here.


class Plan(TimeStampedModel, SoftDeletableModel, Sortable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_plan_id = models.CharField(max_length=256, null=True, blank=True)
    application = models.CharField(max_length=100, choices=APPLICATION_FOR_STRIPE)
    name = models.TextField()
    type = models.CharField(max_length=100, choices=PLAN_TYPE)
    description = models.TextField(null=True, default=None, blank=True)
    criteria = ArrayField(models.CharField(max_length=256), default=list)
    price = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    period = models.CharField(
        max_length=100, choices=PERIOD_FOR_STRIPE_CHARGING, null=True, blank=True
    )
    trial_days = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    order = models.IntegerField(default=1)
    max_internal_users = models.IntegerField(default=-1, null=True, blank=True)
    max_external_users = models.IntegerField(default=-1, null=True, blank=True)
    max_workspaces = models.IntegerField(default=-1, null=True, blank=True)

    enabled = models.BooleanField(default=True)

    class Meta(Sortable.Meta):
        indexes = [
            models.Index(fields=["external_plan_id"]),
        ]

    def __str__(self):
        return f"{self.application} - {self.name}"

    def get_tenancy_config(self) -> List[dict]:
        _fields = ["max_internal_users", "max_external_users", "max_workspaces"]
        config = {_key: getattr(self, _key, None) for _key in _fields}
        return [parse_key_value_label(_key, config.get(_key, None)) for _key in _fields]

    def get_daily_limitation_config(self) -> List[Union[dict, None]]:
        if self.application == APP_TRANSIT:
            return []

        if self.application == APP_MWRW:
            _fields = MapWatcherConfig.get_daily_limitation_config_fields()
            if self.type == PLAN_CUSTOM_ON_DEMAND:
                config = MapWatcherConfigOnDemand.objects.get(
                    plan_id=self.id
                ).daily_limitation
            else:
                config = MapWatcherConfig.objects.get(
                    type__exact=self.type
                ).daily_limitation

            return [
                parse_key_value_label(_key, config.get(_key, None)) for _key in _fields
            ]

        return []

    def get_plan_service_config(self):
        if self.application == APP_TRANSIT:
            return []

        if self.application == APP_MWRW:
            _fields = MapWatcherConfig.get_plan_service_config_fields()
            if self.type == PLAN_CUSTOM_ON_DEMAND:
                config = MapWatcherConfigOnDemand.objects.get(
                    plan_id=self.id
                ).plan_config_on_demand
            else:
                config = MapWatcherConfig.objects.get(type__exact=self.type).plan_config
            return [
                parse_key_value_label(_key, config.get(_key, None)) for _key in _fields
            ]

        return []


class StripeCustomer(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_stripe_id = models.CharField(max_length=100)


class Subscription(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    application = models.CharField(
        max_length=100, choices=APPLICATION_FOR_STRIPE, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    external_subscription_id = models.CharField(max_length=100, null=True)
    expired_in = models.DateTimeField(null=True, default=None)
    amount = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    status = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=False)
    mode = models.CharField(null=True, choices=SUBSCRIPTION_MODE, max_length=10)

    def __str__(self):
        return f"{self.plan.name} - {self.organization.name} - {self.id}"

    class Meta:
        indexes = [
            models.Index(fields=["external_subscription_id"]),
        ]

    @property
    def statuses_subscription(self):
        return ["customer.subscription.updated", "customer.subscription.deleted"]

    def subscriber(self):
        return self.user.email


class SubscriptionActivity(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, choices=SUBSCRIPTION_ACTIVITY)
    data = models.JSONField(null=True, blank=True, default=None)


class SubscriptionCouponCode(TimeStampedModel):
    """
    the coupon code
    which is applied for the current subscription cycle
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    internal_coupon_id = models.IntegerField(editable=False)

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    user_redeemed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    duration_mode = models.CharField(max_length=100, choices=COUPON_DURATION_MODE)
    #
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    discount_id = models.CharField(max_length=100)
    coupon_promotion_code = models.CharField(max_length=100)
    amount_off = models.DecimalField(decimal_places=2, max_digits=6, null=True)  # dollars
    percent_off = models.IntegerField(null=True, validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])
    is_valid = models.BooleanField()
    is_active = models.BooleanField(default=False)
    raw = models.JSONField()

    class Meta:
        unique_together = (
            (
                "subscription",
                "coupon_promotion_code",
                "internal_coupon_id"
            ),
        )
        indexes = [
            models.Index(fields=["subscription", "is_active"]),
            models.Index(fields=["subscription", "coupon_promotion_code"]),
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if force_insert:
            agg_max = SubscriptionCouponCode.objects.aggregate(max_internal_coupon_id=Max('internal_coupon_id'))
            internal_id = agg_max.get("max_internal_coupon_id", None)
            self.internal_coupon_id = 1 if not internal_id else (internal_id + 1)
        return super().save(force_insert, force_update, using, update_fields)

    def invoice_applied_count(self) -> int:
        return CouponCodeHistory.objects.filter(discount_id=self.discount_id, amount__gt=0).count()


class CouponCodeHistory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount_id = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=6)  # dollars

    class Meta:
        indexes = [
            models.Index(fields=["discount_id"])
        ]


class Transaction(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=100)
    external_subscription_id = models.CharField(max_length=100, null=True)
    raw_data = models.JSONField(null=True, blank=True, default=None)
    object_type = models.CharField(max_length=100, null=True)
    external_created_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=100, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["external_subscription_id", "transaction_type"])
        ]


class ApprovalOrganizationalPayment(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE)
    max_internal_users = models.IntegerField(null=True, blank=True)
    max_external_users = models.IntegerField(null=True, blank=True)
    max_workspaces = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.organization.name}"

    def get_config(self):
        if self.subscription.application == APP_TRANSIT:
            return None

        if self.subscription.application == APP_MWRW:
            try:
                saved_config = ApprovalOrganizationalServiceConfig.objects.get(
                    organization_id=self.organization_id
                )
                return saved_config.config
            except ApprovalOrganizationalServiceConfig.DoesNotExist:
                return None

        return None


class ApprovalOrganizationalServiceConfig(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    config = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.organization.name


class MapWatcherConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100, choices=PLAN_TYPE, unique=True, null=False)

    plan_config = models.JSONField(default=dict)
    daily_limitation = models.JSONField(default=dict)

    def __str__(self):
        return self.type

    @staticmethod
    def get_plan_service_config_fields():
        return [
            "plan_max_of_asin_for_amazon",
            "plan_max_of_asin_for_google_shopping",
            "plan_max_of_asin_for_walmart",
            "plan_max_of_reports",
            "plan_max_of_reports_with_amazon",
            "plan_max_of_reports_with_google_shopping",
            "plan_max_of_reports_with_walmart",
            "allowed_amazon_marketplaces",
            "allowed_walmart_marketplaces",
            "seller_enforcement_enabled",
            "seller_investigation_dashboard",
            "data_lifetime",
        ]

    @staticmethod
    def get_daily_limitation_config_fields():
        return [
            "daily_max_of_amazon_scraping",
            "daily_max_of_amazon_inventory_scraping",
            "daily_max_of_google_shopping_scraping",
            "daily_max_of_walmart_scraping",
            "daily_max_of_amazon_screenshot",
            "daily_max_of_google_screenshot",
            "daily_max_of_walmart_screenshot",
            "daily_max_of_retry_per_report",
        ]

    @staticmethod
    def get_tenancy_config_fields():
        return ["max_workspaces", "max_internal_users", "max_external_users"]


class MapWatcherConfigOnDemand(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    tenancy_on_demand = models.JSONField()
    plan_config_on_demand = models.JSONField()
    daily_limitation = models.JSONField()

    is_created_on_stripe = models.BooleanField(default=False)
    price = models.FloatField()  # USD
    name = models.CharField(max_length=256)

    trial_days = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    plan = models.OneToOneField(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    application = models.CharField(max_length=100, choices=APPLICATION_FOR_STRIPE)


class FundPackage(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_fund_package_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    balance = models.BigIntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name


# class OrganizationBalance(TimeStampedModel, SoftDeletableModel):
#     # TODO
#     # Remove
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
#     application = models.CharField(max_length=100, choices=APPLICATION)
#     balance_type = models.CharField(max_length=100, choices=BALANCE_TYPE)
#     balance_subscription = models.BigIntegerField()
#     balance_fund = models.BigIntegerField()
#     meta = models.JSONField(default=dict)
#
#     def __str__(self) -> str:
#         return f"{self.organization.name} - {self.application}"
#
#     class Meta:
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(balance_subscription__gte="0"),
#                 name="balance_subscription_non_negative",
#             ),
#         ]
#
#     @property
#     def available_balance(self) -> int:
#         return sum([self.balance_subscription, self.balance_fund])
#
#     @property
#     def description(self):
#         if self.balance_type == BALANCE_SYSTEM_UNIT:
#             return "accounting by system unit count"
#         return "accounting by currency unit (cent)"
#
#
# class BalanceTransaction(TimeStampedModel, SoftDeletableModel):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     organization_balance = models.ForeignKey(
#         OrganizationBalance, on_delete=models.CASCADE
#     )
#     amount = models.BigIntegerField()
#     source = models.CharField(max_length=100, choices=TRANSACTION_TYPE)
#     user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
#     meta = models.JSONField(default=dict)
#     description = models.TextField(null=True)
#
#     class Meta:
#         indexes = [
#             models.Index(fields=["organization_balance"]),
#             models.Index(fields=["organization_balance", "source"]),
#             models.Index(fields=["organization_balance", "source", "created"]),
#         ]
#
#     @property
#     def stripe_hosted_url(self):
#         return (
#             self.meta.get("hosted_invoice_url")
#             if self.meta.get("hosted_invoice_url")
#             else self.meta.get("receipt_url")
#         )
#
#     @classmethod
#     def stripe_host_url_from_meta(cls, meta):
#         return (
#             meta.get("hosted_invoice_url")
#             if meta.get("hosted_invoice_url")
#             else meta.get("receipt_url")
#         )
#
#     sql_view_daily = """
#     SELECT
#         row_number() OVER () AS id,
#         sub.organization_balance_id,
#         sub.date as date,
#         sub.source,
#         SUM(sub.amount) as amount,
#         json_agg(sub.*) as group_items
#     FROM (
#         SELECT
#             transaction.organization_balance_id,
#             transaction.source,
#             transaction.amount,
#             lateral_date.date as date,
#             transaction.user_id,
#             transaction.meta,
#             transaction.description,
#             transaction.id,
#             transaction.created
#         FROM payments_balancetransaction as transaction
#         LEFT JOIN LATERAL (
#             SELECT DATE(created) as date
#         ) as lateral_date ON TRUE
#     ) as sub
#     GROUP BY
#         sub.organization_balance_id,
#         sub.date,
#         sub.source
#     """
#
#
# class BalanceTransactionDaily(pg.View):
#     # TODO
#     # Remove
#     organization_balance = models.ForeignKey(
#         OrganizationBalance, on_delete=models.CASCADE
#     )
#     amount = models.BigIntegerField()
#     source = models.CharField(max_length=100, choices=TRANSACTION_TYPE)
#     date = models.DateField()
#     group_items = models.JSONField()
#     sql = BalanceTransaction.sql_view_daily
#
#     class Meta:
#         managed = False
#         db_table = "payments_balance_transaction_daily"
#
#
# class ServiceBalanceSubmission(TimeStampedModel, SoftDeletableModel):
#     # TODO
#     # Remove
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     service_key = models.CharField(max_length=100)
#     quantity = models.IntegerField(validators=[MinValueValidator(1)])
#     application = models.CharField(max_length=100, choices=APPLICATION)
#     description = models.CharField(max_length=256, null=True)


# keep changes
auditlog.register(ApprovalOrganizationalServiceConfig)
