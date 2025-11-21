from django.urls import path

from app.payments.sub_views import coupon as coupon_views
from app.payments.sub_views.coupon import ApplyNewPromoCodeView

urlpatterns = [
    path(
        "organizations/<uuid:organization_id>/subscription/coupons/",
        coupon_views.ListCouponsView.as_view(),
        name="get-organization-coupon",
    ),
    path(
        "organizations/<uuid:organization_id>/subscription/coupons/apply/",
        ApplyNewPromoCodeView.as_view(),
        name="subscription-apply-promo-code"
    )
]
