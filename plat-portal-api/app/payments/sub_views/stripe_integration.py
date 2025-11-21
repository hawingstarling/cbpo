import time

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe.error import SignatureVerificationError

from app.core.exceptions import InvalidParameterException
from app.core.logger import logger
from app.payments.config import (
    ACTIVITY_GRADE_CHANGE,
    APP_MWRW,
    APP_TRANSIT, ACTIVITY_PREVIEW_NEW_PLAN, ACTIVITY_UNSUBSCRIBE, ACTIVITY_CHANGE_DEFAULT_PAYMENT,
    ACTIVITY_DELETE_PAYMENT_METHOD
)
from app.payments.exceptions import HandleSubscriptionOnlyException
from app.payments.models import (
    ApprovalOrganizationalPayment,
    ApprovalOrganizationalServiceConfig,
    StripeCustomer,
    Subscription,
)
from app.payments.serializers import (
    SubscriptionSerializer,
    PlanConfigSerializer,
    MwPlanConfigSerializer,
    TransitPlanConfigSerializer,
)
from app.payments.serializers_stripe_integration import (
    CreateCheckoutSessionSerializer,
    CreateCheckoutSessionForGradeChangesSerializer,
    CreateCheckoutSessionAddingFundPackageSerializer,
    CreateCheckoutSessionSetupPaymentIntentSerializer,
    DeleteSubscriptionPaymentMethodSerializer,
    SetDefaultSubscriptionPaymentMethodSerializer,
    PaymentMethodSerializer,
)
from app.payments.services.stripe_invoice import StripeInvoiceService
from app.payments.services.stripe_object_type_handler import StripeObjectTypeHandler
from app.payments.services.stripe_payment_methods import (
    StripePaymentMethods,
)
from app.payments.services.utils import (
    StripeApiServices,
    notify_grade_changes,
    warn_resource_in_organization,
    get_exclude_condition,
)
from app.payments.tasks import cover_health_stripe_subscription_status, subscription_activity_tracking
from app.permission.models import Permission
from app.permission.services.compose_permission_service import ComposePermissionService
from app.tenancies.models import Organization
from app.tenancies.models import OrganizationResourceProxy
from app.tenancies.permissions import IsOwnerOrAdminOrganizationPermission
from app.tenancies.serializers import UserSerializer

TAG_NAME = "stripe"


class StripeWebHookView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        try:
            event = StripeApiServices.verify_data_from_event_webhook(request)
        except SignatureVerificationError as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            return Response(status=400)
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            raise e

        event_type = event["type"]
        data = event["data"]["object"]
        try:
            handler = StripeObjectTypeHandler(event_type=event_type, data=data)
            handler.handle()
        except HandleSubscriptionOnlyException:
            pass
        except Exception as err:
            raise err
        return Response(status=200)


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


class CreateCheckoutSessionView(GetOrganizationMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = CreateCheckoutSessionSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        org = self.get_organization

        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data.get("plan")
        trial_period_days = serializer.validated_data.get("trial_period_days", 0)
        subscription_data = {
            # deprecated -> use line_items
            "items": [{"plan": plan.external_plan_id}],
        }
        if trial_period_days > 0:
            subscription_data.update({"trial_period_days": trial_period_days})

        try:
            res = StripeApiServices.create_checkout_session(
                organization_id=str(org.id),
                customer_stripe_id=serializer.validated_data.get("customer_stripe_id"),
                plan_id=str(plan.id),
                application=plan.application,
                mode=serializer.validated_data.get("mode", None),
                external_plan_id=plan.external_plan_id,
                success_url=serializer.validated_data["success_callback_url"],
                cancel_url=serializer.validated_data["cancel_callback_url"],
                subscription_data=subscription_data,
                user_id=str(request.user.id),
                allow_promotion_codes=serializer.validated_data.get(
                    "allow_promotion_codes", False
                ),
            )
            # celery is required
            if settings.IS_CELERY_ENABLED:
                cover_health_stripe_subscription_status.apply_async(
                    kwargs={
                        "checkout_session_id": res.get("sessionId"),
                        "organization_id": str(org.id),
                        "type": "subscription",
                    },
                    countdown=(60 * 3),
                )
            return Response(
                res,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            raise e


class GradeChangesView(GetOrganizationMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = CreateCheckoutSessionForGradeChangesSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        org = self.get_organization  # noqa

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data.get("plan")
        subscription = serializer.validated_data.get("subscription")
        subscription_data_stripe = serializer.validated_data.get(
            "subscription_data_stripe"
        )

        sub_item = subscription_data_stripe["items"]["data"][0]["id"]
        new_items_changes = [{"id": sub_item, "price": plan.external_plan_id}]

        current_time_changes = time.time()

        StripeApiServices.modify_subscription(
            external_subscription_id=subscription.external_subscription_id,
            new_items=new_items_changes,
        )

        previous_plan_name = subscription.plan.name
        action = "upgraded" if plan.price > subscription.plan.price else "downgraded"

        if settings.IS_CELERY_ENABLED:
            subscription_activity_tracking.apply_async(
                kwargs={
                    "subscription_id": str(subscription.id),
                    "user_id": str(request.user.id),
                    "action": ACTIVITY_GRADE_CHANGE
                }
            )

        subscription.plan_id = plan.id
        subscription.save(update_fields=["plan_id"])

        approval_settings = {
            "subscription_id": subscription.id,
            "max_internal_users": plan.max_internal_users,
            "max_external_users": plan.max_external_users,
            "is_removed": False,
            "max_workspaces": plan.max_workspaces,
        }

        meta_info = {}

        if subscription.application == APP_MWRW:
            serializer = MwPlanConfigSerializer(plan)

            exclude_permission = get_exclude_condition(org_id=org.id)
            if exclude_permission:
                permission_ids = Permission.objects.filter(
                    **exclude_permission
                ).values_list("id", flat=True)
                org_resource_proxy = OrganizationResourceProxy.objects.get(id=org.id)
                ComposePermissionService.delete_saved_override_permission(
                    object_reference=org_resource_proxy.all_org_and_client_users,
                    permission_ids=permission_ids,
                )

        elif subscription.application == APP_TRANSIT:
            serializer = TransitPlanConfigSerializer(plan)
        else:
            serializer = PlanConfigSerializer(plan)

        ApprovalOrganizationalPayment.all_objects.update_or_create(
            organization_id=org.id, defaults=approval_settings
        )
        ApprovalOrganizationalServiceConfig.all_objects.update_or_create(
            organization=subscription.organization,
            defaults={"config": serializer.data, "is_removed": False},
        )
        notify_grade_changes(
            previous_plan_name=previous_plan_name,
            action=action,
            subscription=subscription,
            time_grade_changes=int(current_time_changes),
            user=request.user,
            subscription_items=new_items_changes,
            meta_info=meta_info,
        )

        subscription_serializer = SubscriptionSerializer(subscription)
        return Response(subscription_serializer.data, status=status.HTTP_200_OK)


class PreviewGradeChangesView(GetOrganizationMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = CreateCheckoutSessionForGradeChangesSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        organization = self.get_organization  # noqa
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data.get("plan")
        subscription = serializer.validated_data.get("subscription")
        subscription_data_stripe = serializer.validated_data.get(
            "subscription_data_stripe"
        )

        sub_item = subscription_data_stripe["items"]["data"][0]["id"]
        new_items_changes = [{"id": sub_item, "price": plan.external_plan_id}]

        proration_date = int(time.time())  # noqa
        incoming_invoice = StripeApiServices.get_incoming_invoice(
            external_subscription_id=subscription.external_subscription_id,
            sub_items=new_items_changes,
            proration_date=proration_date,
        )

        preview_data = StripeInvoiceService(incoming_invoice).output()
        preview_data.update(
            {
                "proration_date": proration_date * 1000,
            }
        )

        try:
            # the initial payment for the subscription
            stripe_customer = StripeCustomer.objects.get(user=subscription.user)
        except Exception as err:
            raise err

        payment_methods = StripePaymentMethods(
            stripe_customer.customer_stripe_id
        ).get_all()

        default_payment_method = subscription_data_stripe.get("default_payment_method")

        if settings.IS_CELERY_ENABLED:
            subscription_activity_tracking.apply_async(
                kwargs={
                    "type": ACTIVITY_PREVIEW_NEW_PLAN,
                    "user_id": str(self.request.user.id),
                    "subscription_id": str(subscription.id),
                    "data": {
                        "new_plan": {
                            "plan_id": str(plan.id),
                            "plan_name": plan.name
                        }
                    }
                }
            )

        return Response(
            {
                "preview_data": preview_data,
                "payment_methods": payment_methods,
                "default_payment_method": default_payment_method,
                "resource_comparison": warn_resource_in_organization(
                    organization=organization, intent_plan=plan
                ),
                "meta": {
                    # "credit": "Upgrading or downgrading does not change your existing credits."
                    # "It will be reloaded on the next payment."
                },
            },
            status=status.HTTP_200_OK,
        )


class CreateCheckoutSessionSetupPaymentIntentView(
    GetOrganizationMixin, generics.GenericAPIView
):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = CreateCheckoutSessionSetupPaymentIntentSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        _ = self.get_organization
        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        try:
            res = StripeApiServices.create_checkout_setup_payment(
                customer_stripe_id=serializer.validated_data["customer_stripe_id"],
                success_url=serializer.validated_data["success_callback_url"],
                cancel_url=serializer.validated_data["cancel_callback_url"],
            )
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            raise e


class CreateCheckoutSessionAddingFundPackageView(
    GetOrganizationMixin, generics.GenericAPIView
):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = CreateCheckoutSessionAddingFundPackageSerializer

    @swagger_auto_schema(tags=[TAG_NAME])
    def post(self, request, *args, **kwargs):
        org = self.get_organization

        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        fund_package = serializer.validated_data.get("fund_package")
        line_items = [{"price": fund_package.external_fund_package_id, "quantity": 1}]

        try:
            res = StripeApiServices.create_checkout_adding_fund(
                organization_id=str(org.id),
                customer_stripe_id=serializer.validated_data.get("customer_stripe_id"),
                success_url=serializer.validated_data["success_callback_url"],
                cancel_url=serializer.validated_data["cancel_callback_url"],
                line_items=line_items,
                user_id=str(request.user.id),
                external_fund_package_id=serializer.validated_data.get(
                    "external_fund_package_id"
                ),
                fund_package_id=serializer.validated_data.get("fund_package_id"),
            )
            return Response(
                res,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            raise e


class ListSubscriptionPaymentMethodsView(GetOrganizationMixin, generics.GenericAPIView):
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrAdminOrganizationPermission,
    )

    @swagger_auto_schema(tags=[TAG_NAME])
    def get(self, request, *args, **kwargs):
        _ = self.get_organization
        serializer = PaymentMethodSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        try:
            payment_methods = StripePaymentMethods(
                stripe_customer_id=serializer.validated_data["customer_stripe_id"]
            ).get_all()
            sub = serializer.validated_data["subscription"]
            user_serializer = UserSerializer(sub.user)

            sub_data = StripeApiServices.retrieve_subscription_data(
                sub.external_subscription_id
            )
            res = {
                "payment_methods": payment_methods,
                "default_payment_method": sub_data.get("default_payment_method"),
                "owner": user_serializer.data,
                "message": "This user is presented as the owner of these payment methods",
            }
        except Subscription.DoesNotExist:
            raise InvalidParameterException(message="invalid subscription id")
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}] {err}")
            raise err
        return Response(res, status=status.HTTP_200_OK)


class ModifySubscriptionPaymentMethodView(
    GetOrganizationMixin, generics.GenericAPIView
):
    permission_classes = (IsAuthenticated, IsOwnerOrAdminOrganizationPermission)
    serializer_class = SetDefaultSubscriptionPaymentMethodSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SetDefaultSubscriptionPaymentMethodSerializer
        return DeleteSubscriptionPaymentMethodSerializer

    @swagger_auto_schema(
        tags=[TAG_NAME], request_body=SetDefaultSubscriptionPaymentMethodSerializer
    )
    def post(self, request, *args, **kwargs):
        _ = self.get_organization
        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        try:
            _ = StripeApiServices.modify_subscription_payment_method(
                external_subscription_id=serializer.validated_data[
                    "external_subscription_id"
                ],
                payment_method_id=serializer.validated_data["payment_method_id"],
            )
            if settings.IS_CELERY_ENABLED:
                subscription_activity_tracking.apply_async(
                    kwargs={
                        "type": ACTIVITY_CHANGE_DEFAULT_PAYMENT,
                        "subscription_id": str(serializer.validated_data["subscription_id"]),
                        "user_id": str(self.request.user.id),
                        "data": {
                            "new_default_payment_method_id": str(serializer.validated_data["payment_method_id"])
                        }
                    }
                )
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] {e}")
            raise e
        return Response(None, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=[TAG_NAME], request_body=DeleteSubscriptionPaymentMethodSerializer
    )
    def delete(self, request, *args, **kwargs):
        _ = self.get_organization
        serializer = self.get_serializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        # delete payment method from customer
        StripeApiServices.delete_subscription_payment_method(
            payment_method_id=serializer.validated_data["payment_method_id"]
        )
        if settings.IS_CELERY_ENABLED:
            subscription_activity_tracking.apply_async(
                kwargs={
                    "type": ACTIVITY_DELETE_PAYMENT_METHOD,
                    "subscription_id": str(serializer.validated_data["subscription_id"]),
                    "user_id": str(self.request.user.id),
                    "data": {
                        "delete_payment_method_id": str(serializer.validated_data["payment_method_id"])
                    }
                }
            )
        return Response(None, status=status.HTTP_204_NO_CONTENT)
