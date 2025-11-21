from django.urls import include, path

from app.tenancies.sub_views.rest_auth import CustomPasswordResetView
from app.tenancies.sub_views.rest_auth import UserResetPasswordIdentityView
from app.core.views import CheckServicesStatusView

urlpatterns = [
    path(
        "rest-auth/password/reset/",
        CustomPasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "rest-auth/password/reset/identity/",
        UserResetPasswordIdentityView.as_view(),
        name="password-reset-identity",
    ),
    # url("rest-auth/", include("rest_auth.urls")),
    path("rest-auth/", include("dj_rest_auth.urls")),
    path("social-auth/", include("app.social_auth.urls")),
    path(
        "healths/",
        CheckServicesStatusView.as_view(),
        name="services-status",
    ),
    path("", include("app.tenancies.urls")),
    path("", include("app.permission.urls")),
    path("", include("app.payments.urls")),
    path("", include("app.app_setting.urls")),
]
