import uuid
from typing import List, Optional

from allauth.utils import generate_unique_username
from auditlog.registry import auditlog
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField
from itsdangerous import URLSafeTimedSerializer
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.utils.translation import gettext_lazy as _

from config.settings.common import SECRET_KEY
from .config_app_and_module import LIST_APP_CONFIG
from .config_static_variable import (
    MODULE_ENUM,
    TYPE_NOTIFICATION,
    NOTIFICATION_STATUS,
    MEMBER_STATUS,
    ACTION_ACTIVITY, TIME_FOR_TOKEN_EXPIRED, DAYS_EXPIRED,
)
from .utils import generate_6_digits_code, generate_token_otp_code


class User(AbstractUser, TimeStampedModel, SoftDeletableModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, editable=True)
    email_verified_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=13)
    avatar = models.CharField(max_length=250)
    enabled = models.BooleanField(default=True)
    can_create_client = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def name(self):
        name = "%s %s" % (self.first_name, self.last_name)
        if not name.strip():
            name = self.username  # "User #%s" % self.pk
        return name

    @property
    def id(self):
        return self.user_id

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = generate_unique_username(
                [self.first_name, self.last_name, self.email, self.username, "user"]
            )

        self.first_name = " ".join(self.first_name.split())
        self.last_name = " ".join(self.last_name.split())
        return super().save(*args, **kwargs)


class Organization(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    logo = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "name",
            "owner",
        )
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name + " - " + str(self.id)


class Client(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    name = models.TextField()
    logo = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dashboard_button_color = models.CharField(max_length=50, default="#1985ac")
    account_manager = models.CharField(max_length=200, null=True, editable=True)
    special_project_manager = models.CharField(max_length=200, null=True, editable=True)
    extra_information = models.JSONField(null=True)

    all_objects = models.Manager()

    def __str__(self):
        return self.name + " - " + str(self.id)

    class Meta:
        unique_together = (
            "name",
            "organization",
        )


class ClientModule(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    module = models.CharField(max_length=50, choices=MODULE_ENUM)

    all_objects = models.Manager()

    class Meta:
        unique_together = (
            "client",
            "module",
        )

    def __str__(self):
        name = str(self.id) + " - " + self.client.name + " - " + self.module
        return name


class Role(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ActiveMemberManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_removed=False, user__is_active=True)


class OrganizationUser(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=MEMBER_STATUS, default=MEMBER_STATUS[0][0]
    )
    last_active = models.DateTimeField(_('last login'), blank=True, null=True)

    all_objects = models.Manager()
    # override ORM for active member only
    objects = ActiveMemberManager()

    class Meta:
        unique_together = (
            "organization",
            "user",
        )

    def __str__(self):
        return "{username} - {organization} - {role}".format(
            username=self.user.username, organization=self.organization, role=self.role
        )

    def is_admin_or_manager(self):
        if (
                self.role.key == "ADMIN"
                or self.role.key == "MANAGER"
                or self.role.key == "OWNER"
        ):
            return True
        return False

    def is_owner(self):
        if self.role.key == "OWNER":
            return True
        return False

    def pending_to_member(self):
        self.status = MEMBER_STATUS[0][0]
        self.save()

    def is_pending(self):
        return True if self.status == MEMBER_STATUS[1][0] else False

    @property
    def is_external_user(self):
        """
        kind of user
        who is in WS only and does ont have resource in the ORG
        Returns:
        """
        return True if self.role.key == "CLIENT" else False


class UserClient(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=MEMBER_STATUS, default=MEMBER_STATUS[0][0]
    )
    last_active = models.DateTimeField(_('last login'), blank=True, null=True)

    all_objects = models.Manager()
    # override ORM for active member only
    objects = ActiveMemberManager()

    class Meta:
        unique_together = (
            "client",
            "user",
        )

    def __str__(self):
        return self.user.username + " - " + str(self.client)

    def is_admin_or_manager(self):
        if (
                self.role.key == "ADMIN"
                or self.role.key == "MANAGER"
                or self.role.key == "OWNER"
        ):
            return True
        return False

    def is_owner(self):
        if self.role.key == "OWNER":
            return True
        return False

    def pending_to_member(self):
        self.status = MEMBER_STATUS[0][0]
        self.save()

    def is_pending(self):
        return True if self.status == MEMBER_STATUS[1][0] else False


class UserOTP(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    token = models.TextField()
    verified = models.BooleanField(default=False)
    count = models.IntegerField(default=0)

    def reset_code(self):
        self.code = generate_6_digits_code()
        self.token = generate_token_otp_code(self.user)
        self.save()

    def matching_code(self, input_code):
        if int(input_code) != int(self.code):
            return False
        return True

    def reset_after_verified(self):
        self.count = 0
        self.verified = True
        self.save()

    @property
    def get_code(self):
        return self.code

    @property
    def get_token(self):
        return self.token

    @property
    def get_verified_code(self):
        return self.verified


class Notification(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_NOTIFICATION)
    object_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=50, null=True)
    object = GenericForeignKey("object_type", "object_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    is_seen = models.BooleanField(default=False)
    status = models.CharField(
        max_length=6, choices=NOTIFICATION_STATUS, default=NOTIFICATION_STATUS[0][0]
    )
    meta = models.JSONField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")


class ValidateToken:
    @staticmethod
    def validate_token_otp(token):
        try:
            max_age = 60 * TIME_FOR_TOKEN_EXPIRED
            s = URLSafeTimedSerializer(SECRET_KEY)
            data = s.loads(token, max_age=max_age)
            user_id = data.get("user_id")
            user = User.objects.filter(pk=user_id).first()
            if user:
                return user_id
            return None
        except ImportError:
            return None

    @staticmethod
    def validate_token_invitation_client(token):
        try:
            max_age = 60 * 60 * 24 * DAYS_EXPIRED
            s = URLSafeTimedSerializer(SECRET_KEY)
            loaded_token = s.loads(token, max_age=max_age)
            user_id = loaded_token.get("user_id")
            client_id = loaded_token.get("client_id")
            inviter_id = loaded_token.get("inviter_id")
            user = User.objects.filter(pk=user_id).first()
            client = Client.objects.filter(pk=client_id).first()
            if user and client:
                return user_id, client_id, inviter_id
            return None
        except ImportError:
            return None

    @staticmethod
    def validate_token_invitation_organization(token):
        try:
            max_age = 60 * 60 * 24 * DAYS_EXPIRED
            s = URLSafeTimedSerializer(SECRET_KEY)
            loaded_token = s.loads(token, max_age=max_age)
            user_id = loaded_token.get("user_id")
            organization_id = loaded_token.get("organization_id")
            inviter_id = loaded_token.get("inviter_id")
            user = User.objects.filter(pk=user_id).first()
            organization = Organization.objects.filter(pk=organization_id).first()
            if user and organization:
                return user_id, organization_id, inviter_id
            return None
        except ImportError:
            return None


class Activity(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=50, choices=ACTION_ACTIVITY)
    object_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=50, null=True)
    object = GenericForeignKey("object_type", "object_id")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activity_user"
    )
    data = models.JSONField()

    def __str__(self):
        return "{id} - {user_name} - {action}".format(
            id=self.id, user_name=self.user.username, action=self.action
        )


class AppClientConfig(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app = models.CharField(max_length=50, choices=LIST_APP_CONFIG)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    all_objects = models.Manager()

    class Meta:
        unique_together = ("app", "client")

    def __str__(self):
        return "%s -- %s" % (self.app, self.client.name)


class WhiteListEmail(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Setting(TimeStampedModel):
    name = models.CharField(max_length=100, default="default", unique=True)
    number_org_limit = models.IntegerField(default=10)
    number_ws_limit = models.IntegerField(default=30)
    emails = ArrayField(models.EmailField(), default=list, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class OrganizationResourceProxy(Organization):
    class Meta:
        proxy = True

    @property
    def organization_users(self) -> List[Optional[OrganizationUser]]:
        return OrganizationUser.objects.filter(organization=self)

    @property
    def client_users(self) -> List[Optional[UserClient]]:
        clients = Client.objects.filter(organization=self)
        return UserClient.objects.filter(client__in=clients)

    @property
    def all_org_and_client_users(self):
        return [*self.organization_users, *self.client_users]

    @property
    def clients(self) -> List[Optional[Client]]:
        return Client.objects.filter(organization=self)


auditlog.register(User)
auditlog.register(Client)
auditlog.register(ClientModule)
auditlog.register(UserClient)
auditlog.register(Organization)
auditlog.register(OrganizationUser)
auditlog.register(Activity)
