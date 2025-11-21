from app.payments.sub_urls import common, services_integration, stripe_integration, coupon

urlpatterns = (
    common.urlpatterns
    + services_integration.urlpatterns
    + stripe_integration.urlpatterns
    + coupon.urlpatterns
)
