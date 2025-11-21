from admin_auto_filters.filters import AutocompleteFilter
from adminsortable.admin import SortableAdmin
from django.contrib import admin
from django.contrib import messages
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from app.core.logger import logger
from app.payments.forms import (
    ApprovalConfigServiceForm,
    MapWatcherConfigOnDemandForm,
    TransactionForm,
    MapWatcherConfigForm, SubscriptionCouponUsageForm,
)
from app.payments.models import (
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    MapWatcherConfig,
    MapWatcherConfigOnDemand,
    Plan,
    StripeCustomer,
    Subscription,
    SubscriptionActivity,
    Transaction, SubscriptionCouponCode,
)
from app.payments.services.on_demand_plan import OnDemandPlan
from app.payments.services.utils import StripeApiServices


# Register your models here.


class PlanAdmin(DynamicArrayMixin, SortableAdmin):
    ordering = ("order",)
    list_filter = (
        "application",
        "enabled",
        "type",
    )
    list_display = (
        "application",
        "enabled",
        "name",
        "type",
        "price",
        "period",
        "max_internal_users",
        "max_external_users",
        "max_workspaces",
        "external_plan_id",
    )

    def save_model(self, request, obj, form, change):
        if change and obj.enabled is False:
            exist_subs = Subscription.objects.filter(plan_id=obj.id, is_active=True)
            if exist_subs.count():
                # we should not disable plans what are being used by customers
                return self.message_user(
                    request,
                    "we should not disable plans what are being used by customers",
                    messages.ERROR,
                )

        return super(PlanAdmin, self).save_model(request, obj, form, change)


class SubscriptionAdmin(admin.ModelAdmin):
    list_filter = ("application",)
    search_fields = ("external_subscription_id",)
    list_display = (
        "plan",
        "organization",
        "subscriber",
        "external_subscription_id",
        "expired_in",
        "amount",
        "status",
        "is_active",
    )
    readonly_fields = (
        "user",
        "plan",
        "organization",
        "external_subscription_id",
        "is_removed",
        "amount",
        "expired_in",
        "display_transaction",
    )
    actions = [
        "cancel_subscriptions",
        "force_trial_end_now",
        "force_reset_billing_cycle_now"
    ]

    def display_transaction(self, obj):
        res = Transaction.objects.filter(
            external_subscription_id=obj.external_subscription_id
        ).order_by("external_created_time")
        return ", ".join(tran.transaction_type for tran in res)

    def delete_model(self, request, obj):
        StripeApiServices.cancel_subscription(obj.external_subscription_id)
        ref = ApprovalOrganizationalPayment.objects.get(
            organization_id=obj.organization_id
        )
        ref.delete()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        subscription_ids = [ele.external_subscription_id for ele in queryset]
        for ele in subscription_ids:
            try:
                StripeApiServices.cancel_subscription(ele)
                SubscriptionCouponCode.objects.filter(subscription__external_subscription_id=ele).update(
                    is_active=False)
            except Exception as err:
                logger.error(f"[DJANGO ADMIN] [cancel_subscriptions] {err}")
                pass

        ref_ids = [ele.organization_id for ele in queryset]
        refs = ApprovalOrganizationalPayment.objects.filter(organization_id__in=ref_ids)
        refs.delete()
        super().delete_queryset(request, queryset)

    def cancel_subscriptions(self, request, queryset):
        print(request)
        subscription_ids = [ele.external_subscription_id for ele in queryset]
        for ele in subscription_ids:
            try:
                StripeApiServices.cancel_subscription(ele)
                SubscriptionCouponCode.objects.filter(subscription__external_subscription_id=ele).update(
                    is_active=False)
            except Exception as err:
                logger.error(f"[DJANGO ADMIN] [cancel_subscriptions] {err}")
                pass

    def force_trial_end_now(self, request, queryset):
        print(request)
        subscription_ids = [ele.external_subscription_id for ele in queryset]
        for ele in subscription_ids:
            try:
                StripeApiServices.force_trial_end_now(external_subscription_id=ele)
            except Exception as err:
                logger.error(f"[DJANGO ADMIN] [force_trial_end_now] {err}")
                pass

    def force_reset_billing_cycle_now(self, request, queryset):
        print(request)
        subscription_ids = [ele.external_subscription_id for ele in queryset]
        for ele in subscription_ids:
            try:
                StripeApiServices.force_billing_cycle_now(external_subscription_id=ele)
            except Exception as err:
                logger.error(f"[DJANGO ADMIN] [force_reset_billing_cycle_now] {err}")
                pass

    display_transaction.short_description = "Transactions"
    cancel_subscriptions.short_description = "Cancel these subscriptions"
    force_trial_end_now.short_description = "Force trial end of the subscriptions"
    force_reset_billing_cycle_now.short_description = "Force reset billing cycle"


class SubscriptionActivityAdmin(admin.ModelAdmin):
    search_fields = (
        "subscription__organization__name",
        "user__email",
    )
    list_display = (
        "subscription",
        "user",
        "action",
        "created",
    )
    ordering = (
        "-created",
    )


class TransactionAdmin(admin.ModelAdmin):
    search_fields = ("external_subscription_id",)
    form = TransactionForm
    list_display = (
        "transaction_type",
        "external_subscription_id",
        "object_type",
        "external_created_time",
        "status",
        "created",
    )
    readonly_fields = (
        "external_subscription_id",
        "transaction_type",
        "is_removed",
        "external_created_time",
    )

    ordering = (
        "external_subscription_id",
        "-external_created_time",
    )

    def save_model(self, request, obj, form, change):
        raise Exception("not allowed")


class ApprovalOrganizationalPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "subscription",
        "max_internal_users",
        "max_external_users",
        "max_workspaces",
    )
    readonly_fields = ("organization", "subscription", "is_removed")


class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ("user",)
    readonly_fields = ("user", "customer_stripe_id", "is_removed")


class PlanMapWatcherConfigAdmin(DynamicArrayMixin, admin.ModelAdmin):
    form = MapWatcherConfigForm


class ApprovalOrganizationalServiceConfigAdmin(admin.ModelAdmin):
    form = ApprovalConfigServiceForm


class OrganizationRelatedFilter(AutocompleteFilter):
    title = "Organization"
    field_name = "organization"


class MapWatcherConfigOnDemandAdmin(admin.ModelAdmin):
    form = MapWatcherConfigOnDemandForm
    list_display = (
        "organization",
        "plan",
        "is_created_on_stripe",
    )
    list_filter = ("is_created_on_stripe", OrganizationRelatedFilter)
    autocomplete_fields = ["organization"]
    raw_id_fields = ("organization",)

    actions = ["create_plan_on_stripe"]

    def create_plan_on_stripe(self, request, queryset):
        if len(queryset) > 1:
            return self.message_user(request, "limit one selection", messages.ERROR)

        _demand = queryset[0]
        if _demand.is_created_on_stripe is True:
            return self.message_user(request, "already created", messages.ERROR)

        handler = OnDemandPlan(demand_config_id=_demand.id)
        handler.create()

    create_plan_on_stripe.short_description = "Create plan on stripe"


class SubscriptionCouponUsageAdmin(admin.ModelAdmin):
    search_fields = ("external_subscription_id",)
    form = SubscriptionCouponUsageForm

    list_display = (
        "subscription",
        "coupon_promotion_code",
    )

    def save_model(self, request, obj, form, change):
        raise Exception("not allowed")


admin.site.register(Plan, PlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ApprovalOrganizationalPayment, ApprovalOrganizationalPaymentAdmin)
admin.site.register(StripeCustomer, StripeCustomerAdmin)
admin.site.register(SubscriptionActivity, SubscriptionActivityAdmin)
admin.site.register(MapWatcherConfig, PlanMapWatcherConfigAdmin)
admin.site.register(
    ApprovalOrganizationalServiceConfig, ApprovalOrganizationalServiceConfigAdmin
)
admin.site.register(MapWatcherConfigOnDemand, MapWatcherConfigOnDemandAdmin)
admin.site.register(SubscriptionCouponCode, SubscriptionCouponUsageAdmin)
