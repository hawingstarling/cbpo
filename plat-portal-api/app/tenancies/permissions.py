import logging
from datetime import datetime, timezone

from rest_framework import permissions

from app.payments.models import Subscription
from app.payments.services.utils import (
    check_limit_client_of_organization,
    check_limit_external_users_of_organization,
    check_limit_internal_users_of_organization,
)
from app.tenancies.models import OrganizationUser, Setting, Organization
from app.tenancies.services import (
    OrganizationRoleActionService,
    OrganizationRoleService,
    OrganizationService,
    UserClientService,
)

logger = logging.getLogger(__name__)


class IsAdminManagerOrReadOnlyClient(permissions.BasePermission):
    """
    custom permissions to only admin role or manager role of the client.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request staff member,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only admin or manager of the organization.
        if obj.owner == request.user:
            return True
        return UserClientService.validate_role_admin_or_manager(
            user=request.user, client=obj
        )

    def has_permission(self, request, view):
        # Read permissions are allowed to any request of staff member,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        user = view.get_user()
        client = view.get_client()
        if request.method in permissions.SAFE_METHODS:
            return UserClientService.validate_member_in_client(user, client)

        # Write permissions are only admin or manager of the organization.
        if client.owner == request.user:
            return True
        return UserClientService.validate_role_admin_or_manager(
            user=request.user, client=client
        )


class IsOrganizationUser(permissions.BasePermission):
    def has_permission(self, request, view):
        client = view.get_client()
        if client:
            return UserClientService.validate_role_admin_or_manager(
                request.user, client
            )
        return False


class IsAdminManagerClientModule(permissions.BasePermission):
    """
    custom permissions to only admin or manager of the client to view the list of modules.
    """

    def has_permission(self, request, view):
        client = view.get_client()
        try:
            if client:
                return UserClientService.validate_role_admin_or_manager(
                    request.user, client
                )
        except Exception:
            return False
        return False


class IsOrganizationManagerClientModule(permissions.BasePermission):
    """
    custom permissions to only admin or manager of the client to view the list of modules.
    """

    def has_permission(self, request, view):
        client = view.get_client()
        if client:
            return UserClientService.validate_role_admin_or_manager(
                request.user, client
            )
        return False


class IsUserOrganization(permissions.BasePermission):
    """
    custom permissions to only admin or manager of the client to view the list of modules.
    """

    def has_permission(self, request, view):
        organization = view.get_organization
        return OrganizationService.validate_role_user_organization(
            user=request.user, organization=organization
        )


class IsOrganizationActivity(IsUserOrganization):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        role = view.get_organization_user_role_current()
        return (
                role
                and role.key
                in OrganizationRoleActionService.get_role_action_with_all_organization()
        )


class IsOrganizationAction(IsUserOrganization):
    def has_permission(self, request, view):
        if (
                super().has_permission(request, view)
                and hasattr(request, "method")
                and request.method in permissions.SAFE_METHODS
        ):
            return True
        role = view.get_organization_user_role_current()
        return (
                role
                and role.key
                in OrganizationRoleActionService.get_role_action_with_all_organization()
        )


class IsOrganizationUserAction(IsUserOrganization):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if (
                super().has_permission(request, view)
                and hasattr(request, "method")
                and request.method in permissions.SAFE_METHODS
        ):
            return True
        organization = view.get_organization
        role_user_current = OrganizationRoleService.get_query_set_role_user(
            organization, user=request.user
        ).first()
        key_role_validate = ["OWNER"]
        if role_user_current.role.key in key_role_validate:
            return True
        role_user_request = OrganizationRoleService.get_query_set_role_user(
            organization, user=view.get_user_request
        ).first()
        if role_user_request.role.key in key_role_validate:
            return False
        return True


class IsOrganizationUserActionUpdateRole(IsUserOrganization):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        data = request.data
        organization = view.get_organization
        role_user_current = OrganizationRoleService.get_query_set_role_user(
            organization, user=request.user
        ).first()
        key_role_validate = ["OWNER"]
        if role_user_current.role.key in key_role_validate:
            return True
        role_user_request = OrganizationRoleService.get_query_set_role_user(
            organization, user=view.get_user_request
        ).first()
        if role_user_request.role.key in [
            OrganizationRoleActionService.get_key_owner()
        ] or (
                role_user_request.role.key
                not in OrganizationRoleActionService.get_role_action_with_all_organization()
                and data.get("role_update").upper()
                in [OrganizationRoleActionService.get_key_owner()]
        ):
            return False
        return True


class IsOrganizationUserCreateClient(IsUserOrganization):
    def has_permission(self, request, view):
        if (
                super().has_permission(request, view)
                and hasattr(request, "method")
                and request.method in permissions.SAFE_METHODS
        ):
            return True
        role = view.get_organization_user_role_current()
        return (
                role and role.key in OrganizationRoleActionService.get_role_create_client()
        )


class IsAdminManagerClientModuleOrMyself(permissions.BasePermission):
    def has_permission(self, request, view):
        client = view.get_client()
        user = view.get_user()
        if user == request.user:
            # owner
            return True
        if client:
            return UserClientService.validate_role_admin_or_manager(
                request.user, client
            )
        return False


class UserCanCreateClient(permissions.BasePermission):
    """
    only users have permission 'can_create_client' can create client
    """

    def has_permission(self, request, view):
        if request.user.can_create_client is True:
            return True
        return False


class UserUpdateNotificationPermission(permissions.BasePermission):
    """
    only notification are affected by their owner
    """

    def has_permission(self, request, view):
        notification = view.get_object()
        if notification.user != request.user:
            return False
        return True


class IsOwnerOrAdminOrganizationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            org_user = OrganizationUser.objects.get(
                user=request.user, organization=view.get_organization
            )
            if org_user.role.key in ["OWNER", "ADMIN"]:
                return True
            return False
        except OrganizationUser.DoesNotExist:
            return False


class LimitNewOrgDefaultPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            qs = Organization.objects.filter(owner=request.user)
            setting = Setting.objects.filter(name="default").first()
            assert qs.count() < getattr(setting, "number_org_limit", 10)
            return True
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            return False


class LimitNewClientDefaultPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            org = view.get_organization
            setting = Setting.objects.filter(name="default").first()
            assert org.client_set.count() < getattr(setting, "number_ws_limit", 30), \
                "Limit number of workspace is reached"
            return True
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}] {ex}")
            return False


class _ApprovalSubscriptionPermission(permissions.BasePermission):
    message = "Your request is not accepted. You exceeded the limit possibly."

    def has_permission(self, request, view):
        organization_id = self._get_organization_id(view)
        try:
            subscription = Subscription.objects.get(
                organization_id=organization_id
            )
            """
            if subscription is_active is False and amount is greater
            than 0 and status is canceled
            check remaining time
            """
            if (
                    not subscription.is_active
                    and subscription.amount
                    and subscription.status == "canceled"
            ):
                current_time = datetime.now(tz=timezone.utc)
                if current_time > subscription.expired_in:
                    return False
        except Subscription.DoesNotExist:
            return False
        return self._handler(organization_id) if organization_id else False

    @classmethod
    def _get_organization_id(cls, view):
        raise NotImplementedError

    @classmethod
    def _handler(cls, organization_id: str) -> bool:
        raise NotImplementedError


class LimitInternalUserPermission(_ApprovalSubscriptionPermission):
    """
    adding new users from organization
    they are internal users
    """

    @classmethod
    def _get_organization_id(cls, view):
        org = view.get_organization
        return org.id

    @classmethod
    def _handler(cls, organization_id: str) -> bool:
        return check_limit_internal_users_of_organization(organization_id)


class LimitExternalUserPermission(_ApprovalSubscriptionPermission):
    """
    adding new users from organization
    they are external users
    """

    @classmethod
    def _get_organization_id(cls, view):
        client = view.get_client()
        return client.organization_id

    @classmethod
    def _handler(cls, organization_id: str) -> bool:
        return check_limit_external_users_of_organization(organization_id)


class LimitNewClientFromPermission(_ApprovalSubscriptionPermission):
    """
    limit adding new clients in organization
    """

    @classmethod
    def _get_organization_id(cls, view):
        org = view.get_organization
        return org.id

    @classmethod
    def _handler(cls, organization_id: str) -> bool:
        return check_limit_client_of_organization(organization_id)
