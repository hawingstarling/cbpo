from typing import List

from django.conf import settings

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.exceptions import InvalidParameterException
from app.payments.config import (
    APP_MWRW,
    PLAN_CUSTOM_ON_DEMAND,
    APP_TRANSIT, ACTIVITY_UNSUBSCRIBE,
)
from app.payments.exceptions import (
    HandleSubscriptionOnlyException,
    NotHandleAppException,
)
from app.payments.models import (
    ApprovalOrganizationalPayment,
    Plan,
    Subscription,
    FundPackage,
    MapWatcherConfig,
    MapWatcherConfigOnDemand,
    ApprovalOrganizationalServiceConfig,
)
from app.payments.serializers import (
    ApprovalOrganizationalPaymentSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    FundPackageSerializer,
    PlanConfigSerializer,
    OrganizationSubscriptionConfigSerializer,
    MwPlanConfigSerializer,
    TransitPlanConfigSerializer,
)
from app.payments.serializers_util import MapWatcherConfigSerializer
from app.payments.services.utils import (
    StripeApiServices,
)
from app.payments.tasks import subscription_activity_tracking
from app.tenancies.config_static_variable import IS_MEMBER
from app.tenancies.models import Organization, OrganizationUser
from app.tenancies.permissions import IsOwnerOrAdminOrganizationPermission

TAG_NAME = "payments"


# Create your views here.


class GetOrganizationMixin:
    @property
    def get_organization(self):
        try:
            organization_id = self.kwargs.get("organization_id")  # noqa
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise InvalidParameterException(
                message="parameter 'organization_id' is invalid."
            )


class GetPlansQuerySetMixin:
    @classmethod
    def get_demand_plan_ids(cls, org: Organization, app_filter: str) -> List[str]:
        return MapWatcherConfigOnDemand.objects.filter(
            organization=org,
            plan__isnull=False,
            application=app_filter,
            is_created_on_stripe=True,
        ).values_list("plan__id", flat=True)

    def get_queryset(self):
        app_filter = self.request.query_params.get("app")  # noqa
        _type = self.request.query_params.get("type")  # noqa

        base_cond = {"enabled": True, "application": app_filter}

        if app_filter == APP_MWRW:
            org = self.get_organization  # noqa

            if _type == "basic":
                # return basic plan, not DEMAND
                return (
                    Plan.objects.filter(**base_cond)
                    .exclude(type=PLAN_CUSTOM_ON_DEMAND)
                    .order_by("order")
                )
            elif _type == "customized":
                # return DEMAND plan
                plan_demand_ids = self.get_demand_plan_ids(org, app_filter)
                return Plan.objects.filter(
                    id__in=plan_demand_ids, type=PLAN_CUSTOM_ON_DEMAND, **base_cond
                ).order_by("price")
            else:
                # return basic plans and org customize plans
                basic_plan_ids = (
                    Plan.objects.filter(**base_cond)
                    .exclude(type=PLAN_CUSTOM_ON_DEMAND)
                    .values_list("id", flat=True)
                )
                plan_demand_ids = self.get_demand_plan_ids(org, app_filter)
                return Plan.objects.filter(
                    id__in=[*plan_demand_ids, *basic_plan_ids], **base_cond
                ).order_by("price", "order")

        return (
            Plan.objects.filter(**base_cond)
            .exclude(type__exact=PLAN_CUSTOM_ON_DEMAND)
            .order_by("order")
        )


class ApplicationGETMixin:
    app = openapi.Parameter(
        "app",
        in_=openapi.IN_QUERY,
        description="""filter by app""",
        type=openapi.TYPE_STRING,
    )
    type = openapi.Parameter(
        "type",
        in_=openapi.IN_QUERY,
        description="""
        basic -> basic plan
        customized -> demand plan
        None -> all""",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(tags=[TAG_NAME], manual_parameters=[app, type])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)  # noqa


class TagGETMixin:
    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)  # noqa


class GetListPlanView(
    ApplicationGETMixin,
    GetPlansQuerySetMixin,
    GetOrganizationMixin,
    generics.ListAPIView,
):
    """
    get list plans or plans based on customer demand

    """

    serializer_class = PlanSerializer
    permission_classes = (IsAuthenticated,)


class GetListPlanConfigView(
    ApplicationGETMixin,
    GetPlansQuerySetMixin,
    GetOrganizationMixin,
    generics.ListAPIView,
):
    """
    get list configs from plans
    response based on app param query "app"
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = MwPlanConfigSerializer

    def get_serializer_class(self):
        app = self.request.query_params.get("app")
        if app == APP_TRANSIT:
            return PlanConfigSerializer
        return MwPlanConfigSerializer


class GetListTransitPlanConfigView(TagGETMixin, generics.ListAPIView):
    """
    get list config from Transit Plans
    """

    serializer_class = TransitPlanConfigSerializer
    queryset = Plan.objects.filter(application=APP_TRANSIT).order_by("order")


class GetListMwPlanConfigView(TagGETMixin, GetOrganizationMixin, generics.ListAPIView):
    """
    get list config from Map Watcher Plans
    """

    serializer_class = MwPlanConfigSerializer

    def get_queryset(self):
        plan_demand_ids = MapWatcherConfigOnDemand.objects.filter(
            organization=self.get_organization, plan__isnull=False, application=APP_MWRW
        ).values_list("plan__id", flat=True)
        if len(plan_demand_ids):
            # return whether exist demand plan
            return Plan.objects.filter(
                id__in=plan_demand_ids, application=APP_MWRW
            ).order_by("price")
        return Plan.objects.filter(application=APP_MWRW).order_by("order")


class GetSubscriptionView(GetOrganizationMixin, generics.RetrieveAPIView):
    """
    Get subscription information
    """

    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)  # noqa

    def get_object(self):
        try:
            organization_id = self.kwargs.get("organization_id")
            return Subscription.objects.get(organization=organization_id)
        except Subscription.DoesNotExist:
            raise InvalidParameterException(message="Subscription does not exist")


class OrganizationUnsubscribeView(GetOrganizationMixin, APIView):
    """
    Unsubscribe
    """

    permission_classes = (IsOwnerOrAdminOrganizationPermission,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        subscription = self.get_object()
        if not subscription.external_subscription_id:
            raise HandleSubscriptionOnlyException(
                "Error! It is subscribed by admin, please contact for unsubscription"
            )

        is_success = StripeApiServices.cancel_subscription(
            subscription.external_subscription_id
        )

        if settings.IS_CELERY_ENABLED:
            subscription_activity_tracking.apply_async(
                kwargs={
                    "type": ACTIVITY_UNSUBSCRIBE,
                    "user_id": str(self.request.user.id),
                    "subscription_id": str(subscription.id),
                    "data": {
                        "status": "user requests"
                    }
                }
            )
        if is_success:
            serializer = SubscriptionSerializer(self.get_object())
            if settings.IS_CELERY_ENABLED:
                subscription_activity_tracking.apply_async(
                    kwargs={
                        "type": ACTIVITY_UNSUBSCRIBE,
                        "user_id": str(self.request.user.id),
                        "subscription_id": str(subscription.id),
                        "data": {
                            "status": "success",
                            "subscription": serializer.data
                        }
                    }
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_object(self):
        try:
            organization_id = self.kwargs.get("organization_id")
            subscription = Subscription.objects.get(
                organization=organization_id, user=self.request.user
            )
        except Subscription.DoesNotExist:
            raise HandleSubscriptionOnlyException(
                message="Organization does not have any subscriptions!"
            )

        if subscription.status == "canceled":
            raise HandleSubscriptionOnlyException(
                message="Subscription is already unsubscribed!"
            )

        return subscription


class GetListOrganizationSubscription(generics.ListAPIView):
    """
    Get all subscription config from user request
    now, it is used by TRANSIT APP
    will be removed and use new one as MWRW APP
    TODO: remove and use another as MWRW APP
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ApprovalOrganizationalPaymentSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # role_keys_for_owner_or_admin = (
        #    OrganizationRoleActionService.get_role_action_with_all_organization()
        # )
        # now bypass role user for 2dt request
        # TODO : available for admin or owner only
        # valid_organization_ids = OrganizationUser.objects.filter(
        #     user=self.request.user, status=IS_MEMBER,
        #     role__key__in=role_keys_for_owner_or_admin).values(
        #     'organization_id')

        valid_organization_ids = OrganizationUser.objects.filter(
            user=self.request.user, status=IS_MEMBER
        ).values("organization_id")

        return ApprovalOrganizationalPayment.objects.filter(
            organization__in=valid_organization_ids
        ).order_by("-created")


class GetSubscriptionConfigView(GetOrganizationMixin, generics.RetrieveAPIView):
    """
    Get subscription config
    """

    serializer_class = OrganizationSubscriptionConfigSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super(GetSubscriptionConfigView, self).get(request, *args, **kwargs)

    def get_object(self):
        try:
            return ApprovalOrganizationalServiceConfig.objects.get(
                organization=self.get_organization
            )
        except ApprovalOrganizationalServiceConfig.DoesNotExist:
            raise InvalidParameterException("Invalid organization id")


# class ListBalanceTransactionView(GetOrganizationMixin, generics.ListAPIView):
#     serializer_class = BalanceTransactionDailySerializer
#     permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
#
#     from_date = openapi.Parameter(
#         "from_date",
#         in_=openapi.IN_QUERY,
#         description="""from date""",
#         type=openapi.TYPE_STRING,
#     )
#     to_date = openapi.Parameter(
#         "to_date",
#         in_=openapi.IN_QUERY,
#         description="""to date""",
#         type=openapi.TYPE_STRING,
#     )
#     type = openapi.Parameter(
#         "type",
#         in_=openapi.IN_QUERY,
#         description="type of invoice",
#         type=openapi.TYPE_STRING,
#     )
#     view = openapi.Parameter(
#         "view",
#         in_=openapi.IN_QUERY,
#         description="view of balance transaction",
#         type=openapi.TYPE_STRING,
#     )
#
#     @swagger_auto_schema(
#         tags=[TAG_NAME], manual_parameters=[view, type, from_date, to_date]
#     )
#     def get(self, request, *args, **kwargs):
#         return super(ListBalanceTransactionView, self).get(request, *args, **kwargs)
#
#     def get_serializer_class(self):
#         _view = self.request.query_params.get("view")
#         if _view == "DAILY":
#             return BalanceTransactionDailySerializer
#         return BalanceTransactionSerializer
#
#     def _queryset_for_daily_view(self):
#         org_balance = OrganizationBalance.objects.get(
#             organization=self.get_organization
#         )
#         return BalanceTransactionDaily.objects.filter(
#             organization_balance=org_balance
#         ).order_by("-date")
#
#     def get_queryset(self):
#         _view = self.request.query_params.get("view")
#         if _view == "DAILY":
#             return self._queryset_for_daily_view()
#
#         org_balance = OrganizationBalance.objects.get(
#             organization=self.get_organization
#         )
#         from_date = self.request.query_params.get("from_date")
#         to_date = self.request.query_params.get("to_date")
#         _type = self.request.query_params.get("type")
#
#         if _type in [TRANSACTION_TYPE_CREDIT_USAGE, TRANSACTION_TYPE_USER_PURCHASE]:
#             queryset = BalanceTransaction.objects.filter(
#                 organization_balance_id=org_balance.id, source=_type
#             )
#         else:
#             queryset = BalanceTransaction.objects.filter(
#                 organization_balance_id=org_balance.id
#             )
#
#         if from_date and to_date:
#             fmt = "%Y-%m-%dT%H:%M:%S.%f%z"
#             from_date = datetime.strptime(from_date, fmt)
#             to_date = datetime.strptime(to_date, fmt)
#             return queryset.filter(
#                 Q(created__gte=from_date, created__lte=to_date)
#             ).order_by("-created")
#         return queryset.order_by("-created")


class ListFundPackageView(GetOrganizationMixin, generics.ListAPIView):
    serializer_class = FundPackageSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return FundPackage.objects.all().order_by("created")


class ListServiceConfigView(generics.ListAPIView):
    serializer_class = MapWatcherConfigSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.kwargs.get("app_name") == APP_MWRW:
            return MapWatcherConfigSerializer
        raise NotHandleAppException()

    def get_queryset(self):
        if self.kwargs.get("app_name") == APP_MWRW:
            return MapWatcherConfig.objects.all().order_by("created")
        raise NotHandleAppException()
