from django.urls import path

from app.payments.sub_views.common import OrganizationUnsubscribeView
from app.payments.sub_views.stripe_integration import (
    StripeWebHookView,
    ModifySubscriptionPaymentMethodView,
    CreateCheckoutSessionSetupPaymentIntentView,
    ListSubscriptionPaymentMethodsView,
    CreateCheckoutSessionAddingFundPackageView,
    CreateCheckoutSessionView,
    GradeChangesView,
    PreviewGradeChangesView,
)

urlpatterns = [
    path(
        # webhook
        "stripe/webhook/",
        StripeWebHookView.as_view(),
        name="stripe-web-hook",
    ),
    path(
        # checkout session subscription
        "organizations/<uuid:organization_id>/checkout/",
        CreateCheckoutSessionView.as_view(),
        name="organization-checkout",
    ),
    path(
        # checkout session adding package
        "organizations/<uuid:organization_id>/balance/checkout/",
        CreateCheckoutSessionAddingFundPackageView.as_view(),
        name="organization-checkout-balance",
    ),
    path(
        # checkout session adding new method payment
        "organizations/<uuid:organization_id>/payment-methods/checkout/",
        CreateCheckoutSessionSetupPaymentIntentView.as_view(),
        name="organization-checkout-payment-methods",
    ),
    path(
        # list payment methods
        "organizations/<uuid:organization_id>/payment-methods/",
        ListSubscriptionPaymentMethodsView.as_view(),
        name="organization-list-payment-methods",
    ),
    path(
        # DELETE (delete), POST (set default) payment method
        "organizations/<uuid:organization_id>/payment-methods/modification/",
        ModifySubscriptionPaymentMethodView.as_view(),
        name="organization-modify-payment-methods",
    ),
    path(
        "organizations/<uuid:organization_id>/unsubscription/",
        OrganizationUnsubscribeView.as_view(),
        name="organization-unsubscribe",
    ),
    path(
        # confirm upgrade or downgrade the subscription
        "organizations/<uuid:organization_id>/grade-changes/checkout/",
        GradeChangesView.as_view(),
        name="organization-grade-changes-checkout",
    ),
    path(
        # preview upgrade or downgrade the subscription
        "organizations/<uuid:organization_id>/grade-changes/preview/",
        PreviewGradeChangesView.as_view(),
        name="organization-grade-changes-preview",
    ),
]
