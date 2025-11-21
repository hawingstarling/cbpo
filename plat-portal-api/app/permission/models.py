import uuid

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel

from app.payments.models import ApprovalOrganizationalServiceConfig
from app.payments.services.utils import get_exclude_condition
from app.permission.config_static_varible.common import (
    CUSTOM_ROLE_ACCESS_RULE_ENUM,
    CUSTOM_TYPE_CREATED_ENUM,
    STATUS_PERMISSION_ENUM,
    GROUP_PERMISSION_ENUM,
    PERMISSION_ENUM,
    ROLE_CUSTOM_KEY,
    STATUS_PERMISSION_ALLOW_KEY,
    CUSTOM_TYPE_CREATED_USER_KEY,
    LEVEL_ENUM,
    CLIENT_LEVEL_KEY,
    MODULE_ENUM,
)
from app.tenancies.models import User, OrganizationUser, UserClient


# Create your models here.


class CustomRole(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(
        max_length=10, choices=CUSTOM_ROLE_ACCESS_RULE_ENUM, default=ROLE_CUSTOM_KEY
    )
    name = models.CharField(max_length=100, null=True)
    level = models.CharField(
        max_length=50, choices=LEVEL_ENUM, default=CLIENT_LEVEL_KEY
    )
    # Generic relation [Organization, Client] for custom role
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="org_client_custom_role_fk",
        null=True,
    )
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    #
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # type custom role created by [System, User]
    type_created = models.CharField(
        max_length=10, choices=CUSTOM_TYPE_CREATED_ENUM, default=ROLE_CUSTOM_KEY
    )

    def __str__(self):
        return "{} - {} - {}".format(self.content_object, self.name, self.owner)


class OrgClientCustomRoleUser(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Generic relation [OrganizationUser, ClientUser] for list custom role of User
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="org_client_user_custom_role_fk",
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    #
    custom_role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    priority = models.IntegerField()

    def __str__(self):
        return "{} - {} - {}".format(
            self.content_object, self.custom_role.name, self.priority
        )


class AccessRule(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(
        max_length=50, choices=CUSTOM_ROLE_ACCESS_RULE_ENUM, default=ROLE_CUSTOM_KEY
    )
    name = models.CharField(max_length=100, null=True)
    level = models.CharField(
        max_length=50, choices=LEVEL_ENUM, default=CLIENT_LEVEL_KEY
    )
    # Generic relation [Organization, Client] for access rule
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="org_client_access_rule_fk",
        null=True,
    )
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    # type custom role created by [System, User]
    type_created = models.CharField(
        max_length=10,
        choices=CUSTOM_TYPE_CREATED_ENUM,
        default=CUSTOM_TYPE_CREATED_USER_KEY,
    )
    #
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    module = models.CharField(max_length=50, null=True, default=None)

    def __str__(self):
        return "{} - {} - {}".format(self.content_object, self.name, self.owner)


class CustomRoleAccessRule(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
    access_rule = models.ForeignKey(AccessRule, on_delete=models.CASCADE)
    priority = models.IntegerField()

    def __str__(self):
        return "{} - {} - {}".format(
            self.custom_role.name, self.access_rule.name, self.priority
        )


class Permission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=50, choices=PERMISSION_ENUM, unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(
        max_length=50, choices=MODULE_ENUM, default=MODULE_ENUM[0][0]
    )
    module_name = models.CharField(max_length=100, default=None, null=True)
    group = models.CharField(max_length=50, choices=GROUP_PERMISSION_ENUM)
    group_name = models.CharField(max_length=100, default=None, null=True)
    level = models.CharField(
        max_length=50, choices=LEVEL_ENUM, default=CLIENT_LEVEL_KEY
    )

    def __str__(self):
        return "{} - {}".format(self.group, self.name)


class AccessRulePermission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    access_rule = models.ForeignKey(AccessRule, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_PERMISSION_ENUM,
        default=STATUS_PERMISSION_ALLOW_KEY,
    )

    all_objects = models.Manager()

    def __str__(self):
        return "{} - {} - {}".format(
            self.access_rule.name, self.permission.name, self.status
        )


class OverridingOrgClientUserPermission(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_PERMISSION_ENUM,
        default=STATUS_PERMISSION_ALLOW_KEY,
    )
    # Generic relation [OrganizationUser, ClientUser] for cache last permissions of User
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")


class OrgClientUserPermission(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Generic relation [OrganizationUser, ClientUser] for cache last permissions of User
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="org_client_user_permission_fk",
    )
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    # Permission info
    module = models.CharField(
        max_length=50, choices=MODULE_ENUM, default=MODULE_ENUM[0][0]
    )
    module_name = models.CharField(max_length=100, default=None, null=True)
    group = models.CharField(max_length=50, choices=GROUP_PERMISSION_ENUM)
    key = models.CharField(max_length=50, choices=PERMISSION_ENUM)
    name = models.CharField(max_length=100, default="")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} - {}".format(self.content_object, self.group, self.key)


class OrganizationUserProxy(OrganizationUser):
    custom_roles = GenericRelation(OrgClientCustomRoleUser)
    group_permissions = GenericRelation(OrgClientUserPermission)

    class Meta:
        proxy = True


class ClientUserProxy(UserClient):
    custom_roles = GenericRelation(OrgClientCustomRoleUser)
    group_permissions = GenericRelation(OrgClientUserPermission)
    saved_override_permission = GenericRelation(OverridingOrgClientUserPermission)

    class Meta:
        proxy = True

    def group_permissions_from_settings(self):
        exclude_cond = get_exclude_condition(self.client.organization.id)
        if exclude_cond:
            return self.group_permissions.exclude(**exclude_cond)
        return self.group_permissions
