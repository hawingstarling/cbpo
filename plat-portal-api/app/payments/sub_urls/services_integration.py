from django.urls import path

from app.payments.sub_views import services_integration as service_views

urlpatterns = [
    path(
        "organizations/<uuid:organization_id>/subscription/expiration/",
        service_views.GetExpiredTimeView.as_view(),
        name="get-organization-subscription-expired-time",
    )
]
