from .sub_urls import (
    client,
    common,
    organization,
    rest_auth,
    user,
    activity,
    services_integration,
)

urlpatterns = (
    client.urlpatterns
    + common.urlpatterns
    + organization.urlpatterns
    + rest_auth.urlpatterns
    + user.urlpatterns
    + activity.urlpatterns
    + services_integration.urlpatterns
)
