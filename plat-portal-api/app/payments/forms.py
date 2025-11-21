from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.fields import DynamicArrayField
from django_json_widget.widgets import JSONEditorWidget
from entangled.forms import EntangledModelForm

from app.payments.models import (
    ApprovalOrganizationalServiceConfig,
    MapWatcherConfigOnDemand,
    Transaction,
    MapWatcherConfig, SubscriptionCouponCode,
)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction

        fields = "__all__"
        widgets = {"raw_data": JSONEditorWidget}


class ApprovalConfigServiceForm(forms.ModelForm):
    class Meta:
        model = ApprovalOrganizationalServiceConfig
        fields = "__all__"
        widgets = {"config": JSONEditorWidget}


class __MapWatcherFormMixin(DynamicArrayMixin, EntangledModelForm):
    # DynamicArrayMixin is required for js animation on django admin page

    # service configuration on demand form following plan period
    plan_max_of_asin_for_amazon = fields.IntegerField(required=False)
    plan_max_of_asin_for_google_shopping = fields.IntegerField(required=False)
    plan_max_of_asin_for_walmart = fields.IntegerField(required=False)
    plan_max_of_reports = fields.IntegerField(required=False)
    plan_max_of_reports_with_amazon = fields.IntegerField(required=False)
    plan_max_of_reports_with_google_shopping = fields.IntegerField(required=False)
    plan_max_of_reports_with_walmart = fields.IntegerField(required=False)

    allowed_amazon_marketplaces = DynamicArrayField(
        fields.CharField(max_length=123), default=list, required=False
    )
    allowed_walmart_marketplaces = DynamicArrayField(
        fields.CharField(max_length=123), default=list, required=False
    )
    seller_enforcement_enabled = forms.BooleanField(initial=False, required=False)
    seller_investigation_dashboard = forms.BooleanField(initial=False, required=False)
    data_lifetime = forms.JSONField(initial=None, required=False)

    # daily limitation form
    daily_max_of_amazon_scraping = fields.IntegerField(required=False)
    daily_max_of_amazon_inventory_scraping = fields.IntegerField(required=False)
    daily_max_of_google_shopping_scraping = fields.IntegerField(required=False)
    daily_max_of_walmart_scraping = fields.IntegerField(required=False)
    daily_max_of_amazon_screenshot = fields.IntegerField(required=False)
    daily_max_of_google_screenshot = fields.IntegerField(required=False)
    daily_max_of_walmart_screenshot = fields.IntegerField(required=False)
    daily_max_of_retry_per_report = fields.IntegerField(required=False)

    class Meta:
        pass


class MapWatcherConfigForm(__MapWatcherFormMixin):
    class Meta:
        model = MapWatcherConfig
        entangled_fields = {
            "plan_config": MapWatcherConfig.get_plan_service_config_fields(),
            "daily_limitation": MapWatcherConfig.get_daily_limitation_config_fields(),
        }
        untangled_fields = [
            "type",
        ]


class MapWatcherConfigOnDemandForm(__MapWatcherFormMixin):
    # tenancy_on_demand form
    max_workspaces = fields.IntegerField(required=False)
    max_internal_users = fields.IntegerField(required=False)
    max_external_users = fields.IntegerField(required=False)

    class Meta:
        model = MapWatcherConfigOnDemand
        entangled_fields = {
            "tenancy_on_demand": MapWatcherConfig.get_tenancy_config_fields(),
            "plan_config_on_demand": MapWatcherConfig.get_plan_service_config_fields(),
            "daily_limitation": MapWatcherConfig.get_daily_limitation_config_fields(),
        }
        untangled_fields = [
            "organization",
            "is_created_on_stripe",
            "price",
            "trial_days",
            "name",
            "application",
        ]

    def clean_data_lifetime(self):
        data = self.cleaned_data["data_lifetime"]
        if data is None:
            return None

        try:
            value = data["value"]
            unit = data["unit"]
        except KeyError:
            raise ValidationError(
                "object data_lifetime requires 2 attributes. Eg: {'unit': 'DAY', 'value': 100}"
            )
        if unit not in ["YEAR", "MONTH", "DAY"]:
            raise ValidationError("data_lifetime unit is invalid")
        try:
            if value:
                int(value)
        except Exception:
            raise ValidationError("data_lifetime value is invalid")

        return data


class SubscriptionCouponUsageForm(forms.ModelForm):
    class Meta:
        model = SubscriptionCouponCode

        fields = "__all__"
        widgets = {"raw": JSONEditorWidget}
