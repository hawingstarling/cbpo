from django.urls import path

from app.payments.sub_views.common import (
    GetListOrganizationSubscription,
    GetSubscriptionView,
    GetListPlanConfigView,
    GetSubscriptionConfigView,
    GetListPlanView,
    GetListTransitPlanConfigView,
    GetListMwPlanConfigView,
)

urlpatterns = [
    path(
        # TODO: refactor
        "me/organizations/and/subscriptions/",
        GetListOrganizationSubscription.as_view(),
        name="me-organization-approval-subscriptions",
    ),
    path(
        "organizations/<uuid:organization_id>/subscription/",
        GetSubscriptionView.as_view(),
        name="get-organization-subscription",
    ),
    path(
        "organizations/<uuid:organization_id>/subscription/config/",
        GetSubscriptionConfigView.as_view(),
        name="get-organization-subscription-config",
    ),
    path(
        "organizations/<uuid:organization_id>/plans/",
        GetListPlanView.as_view(),
        name="get-plans",
    ),
    path(
        "organizations/<uuid:organization_id>/config/plans/",
        GetListPlanConfigView.as_view(),
        name="get-plan-configs",
    ),
    path(
        "organizations/<uuid:organization_id>/plans/transit/configs/",
        GetListTransitPlanConfigView.as_view(),
        name="get-plan-transit-configs",
    ),
    path(
        "organizations/<uuid:organization_id>/plans/mwrw/configs/",
        GetListMwPlanConfigView.as_view(),
        name="get-plan-mw-configs",
    ),
]
