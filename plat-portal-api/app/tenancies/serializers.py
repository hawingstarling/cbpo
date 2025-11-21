import re
from calendar import timegm
from datetime import datetime, timedelta

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.utils import get_username_max_length
from django.conf import settings
from django.contrib.auth import signals as auth_signal
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.translation import gettext as _
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenRefreshSlidingSerializer, TokenObtainSerializer
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import SlidingToken, RefreshToken

from app.tenancies.tasks import log_activity_task

from app.core.exceptions import (
    CodeUsedException,
    EmailDoesNotExistException,
    EmailIsUsedException,
    InvalidCodeException,
    InvalidFormatException,
    InvalidTokenException,
    LoginWithoutVerificationException,
    MemberExistsException,
    OwnerRoleUpdateException,
    RegisteredWithoutVerificationException,
    UserIsActivatedException,
)
from app.core.utils import get_app_name_profile
from app.permission.sub_serializers.compose_final_permission_serializer import (
    OrgClientUserPermissionSerializer,
)
from .config_app_and_module import (
    APP_MODULE_BUILD_PROFILE,
    APP_NAME_BUILD_PROFILE, LIST_APP_CONFIG_DICT
)
from .config_static_variable import (
    ACTION_ACTIVITY,
    MEMBER_STATUS,
    MODULE_ENUM,
    REGEX_INTERNAL_USER_DOMAINS,
    TYPE_NOTIFICATION,
    WHITE_LIST_DOMAIN,
    role_name,
)
from .custom_payload_jwt import custom_token_handler
from .models import (
    Activity,
    AppClientConfig,
    Client,
    ClientModule,
    Notification,
    Organization,
    OrganizationUser,
    Role,
    User,
    UserClient,
    WhiteListEmail,
)
from .noti_message_generator_factory import NotificationMessageFactory
from .observer.publisher import publisher
from .activity_services import ActivityService
from .services import (
    ClientModuleService,
    ClientService,
    EmailService,
    OrganizationRoleActionService,
    OrganizationRoleService,
    OrganizationService,
    RoleService,
    UserClientService,
    UserOTPService,
    UserService,
)
from .signals import (
    accepting_invitation_client_signal,
    accepting_invitation_organization_signal,
)
from .utils import (
    generate_random_password,
    get_domain_from_str_url,
    validate_web_base_url,
)
from ..core.context import AppContext
from ..core.helpers import email_address_exists
from ..permission.models import ClientUserProxy


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "logo",
            "active",
            "dashboard_button_color",
            "special_project_manager",
            "account_manager",
            "extra_information",
            "created",
        )
        extra_kwargs = {
            "logo": {"required": False, "allow_blank": True, "allow_null": True},
            "active": {"required": False},
            "account_manager": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "special_project_manager": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "extra_information": {
                "required": False,
                "allow_null": True,
            },
        }

    def validate(self, data):
        # find old value
        request = self.context.get("request", None)
        user = request.user
        pattern = re.compile(REGEX_INTERNAL_USER_DOMAINS)
        if "account_manager" in data and not pattern.search(user.email):
            del data["account_manager"]
        if "special_project_manager" in data and not pattern.search(user.email):
            del data["special_project_manager"]
        return data

    def to_representation(self, instance):
        request = self.context.get("request", None)
        if not request:
            return None
        user = request.user
        data = super(ClientSerializer, self).to_representation(instance)
        pattern = re.compile(REGEX_INTERNAL_USER_DOMAINS)
        if "account_manager" not in data or not pattern.search(user.email):
            data["account_manager"] = None
        if "special_project_manager" not in data or not pattern.search(user.email):
            data["special_project_manager"] = None
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        # check exist organization
        organization = self.context.get("organization")
        with transaction.atomic():  # rollback it something makes db be not unique
            # create client
            client = ClientService.create_client(
                owner=user, organization=organization, **validated_data
            )
            # get role admin
            role = RoleService.role_owner()
            # create user client
            user_client = UserClientService.create_user_client(
                client=client, user=user, role=role
            )
            # create user client module
            ClientModuleService.create_client_module(client=client)
            # create user module permission
        return client


class OrganizationSerializer(serializers.ModelSerializer):
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("id", "name", "logo", "created", "has_access")
        extra_kwargs = {"logo": {"required": False}}

    @property
    def get_user_current(self):
        request = self.context.get("request", None)
        return request.user if request else None

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        with transaction.atomic():  # rollback it something makes db be not unique
            # call service
            organization = OrganizationService.create_organization(
                owner=user, **validated_data
            )
            role_owner = RoleService.role_owner()
            OrganizationService.create_user_organization(
                user=user,
                role=role_owner,
                organization=organization,
                status=MEMBER_STATUS[0][0],
            )
        return organization

    def get_has_access(self, obj) -> bool:
        return OrganizationRoleService.get_permission_access_organization(
            organization=obj, user=self.get_user_current
        )


class UserClientSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)

    class Meta:
        model = UserClient
        fields = "__all__"
        extra_kwargs = {
            "client": {"read_only": True},
            "user": {"read_only": True},
            "role": {"read_only": True},
        }

    def add_member(self, user, client):
        user_client = UserClient.objects.filter(user=user, client=client).first()
        user_client.pending_to_member()
        # update if exist client organization
        organization_user = OrganizationUser.objects.filter(
            user=user,
            organization=client.organization,
            role=RoleService.role_client(),
            status=MEMBER_STATUS[1][0],
        ).first()
        if organization_user:
            organization_user.pending_to_member()
        return user_client

    def create(self, validated_data):
        token = validated_data.get("token")
        user, client, inviter = ClientService.validate_token_invitation(token=token)
        with transaction.atomic():  # rollback it something makes db be not unique
            user_client = self.add_member(user, client)
            accepting_invitation_client_signal.send(
                self.__class__,
                user_id=user.pk,
                client_id=client.pk,
                token=self.validated_data.get("token"),
            )
            UserService.activation(user)
            # log add member activity after user activation
            data = {"Full name": f"{user.first_name} {user.last_name}", "Email": user.email}
            log_activity_task.delay(user_id=inviter.pk if inviter else None, action=ActivityService.action_add_member(),
                                    data=data)
        return user_client

    def is_needed_changing_password(self, user):
        return UserService.is_needed_changing_password(user)


class RoleNameSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    role = serializers.CharField(required=False)

    def validate_role(self, role):
        if not RoleService.validate_role_name(role=role):
            raise serializers.ValidationError("Role name is invalid")
        return role


class InvitationSerializer(RoleNameSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    activation_link_template = serializers.CharField()

    @property
    def context_for_invitation(self):
        return {"is_registration": False}

    def validate_activation_link_template(self, activation_link_template):
        #  validate activation_link_template's domain
        domain = get_domain_from_str_url(activation_link_template)
        flag_domain_accepted = False
        for i in WHITE_LIST_DOMAIN:
            if i in domain:
                flag_domain_accepted = True
                break
        if flag_domain_accepted is False:
            raise InvalidFormatException(
                "activation_link_template's domain is invalid!"
            )
        #  compare end-substring in activation_link_template
        format_required = "?token={token}"
        if (
                activation_link_template[
                -len(format_required): len(activation_link_template)
                ]
                == format_required
        ):
            return activation_link_template
        raise InvalidFormatException("activation_link_template's format is invalid!")

    def create_url_invitation(self, token):
        template_url = self.validated_data.get("activation_link_template")
        url = template_url.replace("{token}", token)
        return url

    def create_for_non_exist_user(self):
        create_user_serializer = CustomRegisterSerializer(
            data=self.get_cleaned_data(), context=self.context_for_invitation
        )
        create_user_serializer.is_valid(raise_exception=True)
        create_user_serializer.save(self.context.get("request"))

    def advanced_validate_exist_user(self):
        #  True -> exist
        #  False -> non-exist
        email = self.validated_data.get("email").lower()
        return User.objects.filter(email=email).exists()

    def get_cleaned_data(self):
        password = generate_random_password()
        first_name, last_name = (
            self.validated_data.get("first_name", ""),
            self.validated_data.get("last_name", ""),
        )
        email = self.validated_data.get("email", "").lower()
        if first_name and last_name != "":
            return {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password1": password,
                "password2": password,
            }
        return {"email": email, "password1": password, "password2": password}


class ClientInvitationSerializer(InvitationSerializer):
    def validate_role(self, role):
        if not super().validate_role(role):
            raise serializers.ValidationError("Role name is invalid")
        return role

    def validate_email(self, email):
        email = email.lower()
        user = User.objects.filter(email=email).first()
        client = self.context.get("client")
        if ClientService.validate_user_exist_in_client(user, client):
            raise MemberExistsException(message="This user already exists")
        return email

    def send_invitation(self, url):
        app_name = self.context.get("app_name")
        app_name = LIST_APP_CONFIG_DICT.get(app_name)
        admin = self.context.get("admin")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        client = self.context.get("client")
        EmailService.send_invitation_member_client(user, url, client, admin, app_name)

    def adding_member(self, user_client_organization=False, is_force_invitation=False):
        client = self.context.get("client")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        if self.validated_data.get("role"):
            # optional data in body request
            # if true -> invite as role assigned
            role = Role.objects.get(key=self.validated_data.get("role").upper())
        else:
            # if false -> role staff is default
            role = RoleService.role_staff()
        if user_client_organization:
            role_organization = RoleService.role_client()
            OrganizationService.create_user_organization(
                organization=client.organization,
                user=user,
                role=role_organization,
                is_force_invitation=is_force_invitation,
            )
        _ = UserClientService.create_user_client(
            client=client,
            user=user,
            role=role,
            invite=True,
            is_force_invitation=is_force_invitation,
        )

    def add_invitation_notification(self, token):
        notification_type = TYPE_NOTIFICATION[0][0]  # ->Invitation
        client = self.context.get("client")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        author = self.context.get("request").user
        meta = {
            "client_id": str(client.pk),
            "type": "client",
            "invitation_token": token,
        }
        UserClientService.adding_notification_model(
            notification_type, client, user, meta, author
        )


class ForceClientInvitationSerializer(ClientInvitationSerializer):
    activation_link_template = None  # bypass inheritance
    password = serializers.CharField()
    web_base_url = serializers.CharField(validators=[validate_web_base_url])

    def create_for_non_exist_user(self):
        # override
        data = self.get_cleaned_data()
        password = self.validated_data.get("password")
        data.update({"password1": password, "password2": password})
        create_user_serializer = CustomRegisterSerializer(
            data=data, context=self.context_for_invitation
        )
        create_user_serializer.is_valid(raise_exception=True)
        create_user_serializer.save(self.context.get("request"))
        email = self.validated_data.get("email")
        verify_email_for_force_invitation = EmailAddress.objects.get(email=email)
        verify_email_for_force_invitation.verified = True
        verify_email_for_force_invitation.save()

    def send_force_invite_notification(self, user_existed: bool):
        app_name = self.context.get("app_name")
        app_name = LIST_APP_CONFIG_DICT.get(app_name)
        admin = self.context.get("admin")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        client = self.context.get("client")
        web_base_url = self.validated_data.get("web_base_url")
        password = self.validated_data.get("password")
        EmailService.send_force_invite_notification_member_client(
            user, password, client, admin, web_base_url, user_existed, app_name
        )


class ClientModulesSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField("get_module_name")

    class Meta:
        model = ClientModule
        fields = (
            "client",
            "module",
            "label",
            "enabled",
        )
        extra_kwargs = {"client": {"required": False}, "module": {"required": False}}

    def get_module_name(self, obj):
        return dict(MODULE_ENUM).get(obj.module, "null")

    def update(self, instance, validated_data):
        flag = instance.enabled
        instance.enabled = not flag
        instance.save()
        return instance


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        email = email.lower()
        if not User.objects.filter(email=email).exists():
            raise EmailDoesNotExistException()
        return email

    def send_email_code(self, user):
        code = UserOTPService.get_or_create_code(user)
        EmailService.send_code_reset_password(user, code)

    def save(self):
        request = self.context.get("request")
        email = request.data.get("email").lower()
        user = User.objects.filter(email=email).first()
        self.send_email_code(user)

    def get_token(self):
        request = self.context.get("request")
        email = request.data.get("email").lower()
        user = User.objects.filter(email=email).first()
        return UserOTPService.get_token(user)


class UserResetPasswordIdentitySerializer(serializers.Serializer):
    code = serializers.CharField()
    token = serializers.CharField()

    def advanced_validation(self):
        token = self.validated_data.get("token")
        code = self.validated_data.get("code")
        user_id = UserOTPService.validate_token_otp(token)
        user = User.objects.filter(pk=user_id).first()
        if user:
            if UserOTPService.verify_used_code(user):
                raise CodeUsedException()
            if UserOTPService.validate_user_code(user, code) is False:
                raise InvalidCodeException()
            return user

    def get_token(self, user):
        UserOTPService.get_or_create_code(user)
        return UserOTPService.get_token(user)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()

    def advanced_validation(self):
        token = self.validated_data.get("token")
        user_id = UserOTPService.validate_token_otp(token)
        user = User.objects.filter(pk=user_id).first()
        if user:
            return user
        raise InvalidTokenException()

    def save(self):
        user = self.advanced_validation()
        UserService.change_password(user, self.validated_data.get("password"))
        UserService.activation(user)
        if UserService.token_exist(user) is True:
            user.auth_token.delete()


class ChaneEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email(self, new_email):
        new_email = new_email.lower()
        if EmailService.validate_new_email(new_email) is False:
            raise EmailIsUsedException()
        return new_email

    def send_email_code(self, user):
        code = UserOTPService.get_or_create_code(user)
        EmailService.send_code_changing_email(user, code)


class ChangeEmailConfirmSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "code",
        )

    def validate_code(self, code):
        request = self.context.get("request")
        if UserOTPService.verify_used_code(request.user) is True:
            raise CodeUsedException()
        if UserOTPService.validate_user_code(request.user, code) is False:
            raise InvalidCodeException()
        return code

    def send_change_email_successfully(self, user, new_email):
        EmailService.send_change_email_successfully(user, new_email)

    def perform_save(self):
        user = self.context.get("request").user
        new_email = self.validated_data.get("email").lower()
        with transaction.atomic():
            self.send_change_email_successfully(user, new_email)
            UserService.change_email_address(user, new_email)
            self.save()
            UserOTPService.reset_after_verified(user)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "enabled",
            "username",
            "password",
            "avatar",
            "last_login"
        )
        extra_kwargs = {"password": {"write_only": True}}


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            "key",
            "name",
        )


class UserClientListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserClient
        fields = (
            "id",
            "status",
            "last_active",
            "role",
            "user",
            "created",
        )


class UserRegisterActivationSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    def validate_code(self, code):
        request = self.context.get("request")
        if UserOTPService.validate_user_code(request.user, code) is False:
            raise InvalidCodeException()
        return code

    def save(self):
        request = self.context.get("request")
        UserService.activation(request.user)
        UserOTPService.reset_after_verified(request.user)


class UserReSendActivationCodeSerializer(serializers.Serializer):
    def is_activated(self, user):
        if UserService.is_activated(user) is True:
            raise UserIsActivatedException()

    def send_email_code(self, user):
        code = UserOTPService.get_or_create_code(user)
        EmailService.send_code_activation_user(user, code)


class CustomRegisterSerializer(RegisterSerializer):
    app = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(
        required=False,
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
    )

    def send_email_activation(self, user):
        code = UserOTPService.get_or_create_code(user)
        EmailService.send_code_activation_user(user, code)

    def get_cleaned_data(self):
        return {
            "app": self.validated_data.get("app", ""),
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email).lower()
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                user = User.objects.get(email=email)
                # user is already registered but not verify email
                if UserService.is_activated(user) is False:
                    raise RegisteredWithoutVerificationException()

                raise serializers.ValidationError(
                    "A user is already registered with this e-mail address."
                )

        # checking white list of email for registration transit app
        # invitation -> bypass
        is_registration = self.context.get("is_registration", True)
        if settings.ONLY_ALLOW_REGISTRATION_FOR_WHITE_LISTED_EMAILS and is_registration:
            try:
                WhiteListEmail.objects.get(email=email)
            except WhiteListEmail.DoesNotExist:
                raise serializers.ValidationError(
                    "The email is not in the white list for registration"
                )
        return email


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "can_create_client",
        )
        read_only_fields = ("email",)
        extra_kwargs = {
            "avatar": {
                "required": False,
                "allow_blank": True,
            }
        }


class _OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = ("is_removed",)


class UserClientSettingDataSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()
    client_modules = serializers.SerializerMethodField()
    client_information = serializers.SerializerMethodField()
    organization_information = serializers.SerializerMethodField()

    class Meta:
        model = UserClient
        fields = (
            "id",
            "status",
            "role",
            "user",
            "client_information",
            "organization_information",
            "client_modules",
            "permissions",
        )

    @property
    def get_modules_app_prodiles(self):
        return APP_MODULE_BUILD_PROFILE[get_app_name_profile()]

    def get_permissions(self, obj):
        # query_set, _ = ComposePermissionService.get_client_user_settings_permissions(
        #     client_id=obj.client.id, user_id=obj.user.pk
        # )
        user_client_proxy = ClientUserProxy.objects.get(id=obj.id)
        query_set = user_client_proxy.group_permissions_from_settings().all()
        modules_enabled = AppContext().instance().module_enabled(str(obj.client.id))
        for per in query_set:
            if per.module not in modules_enabled:
                per.enabled = False
        serializer = OrgClientUserPermissionSerializer(query_set, many=True)
        return serializer.data

    def get_client_modules(self, obj):
        #
        query_set = ClientModule.objects.filter(
            client=obj.client, module__in=self.get_modules_app_prodiles
        ).all()
        serializer = ClientModulesSerializer(query_set, many=True)
        return serializer.data

    def get_client_information(self, obj):
        serializer = ClientSerializer(obj.client, many=False, context=self.context)
        return serializer.data

    def get_organization_information(self, obj):
        serializer = _OrganizationSerializer(obj.client.organization, many=False)
        return serializer.data


class AllUserClientSettingDataSerializer(UserClientSettingDataSerializer):
    class Meta(UserClientSettingDataSerializer.Meta):
        fields = (
            "id",
            "status",
            "role",
            "user",
            "client_information",
            "client_modules",
        )


class CustomRefreshJSONWebTokenSerializer(TokenRefreshSlidingSerializer):
    def _check_user(self, payload):
        username = payload.get(api_settings.USER_ID_FIELD)

        if not username:
            msg = _('Invalid payload.')
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise serializers.ValidationError(msg)

        return user

    def validate(self, attrs):
        token = self.token_class(attrs["token"])

        payload = token.payload
        user = self._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get("iat")

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.REFRESH_TOKEN_LIFETIME

            if isinstance(refresh_limit, timedelta):
                refresh_limit = refresh_limit.days * 24 * 3600 + refresh_limit.seconds

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _("Refresh has expired.")
                raise serializers.ValidationError(msg)
        else:
            msg = _("orig_iat field is required.")
            raise serializers.ValidationError(msg)

        client_id = payload.get("client_id", None)
        client = Client.objects.filter(pk=client_id).first()

        user_client = UserClient.objects.filter(user=user, client=client).first()

        token = custom_token_handler(
            user=user,
            client=client,
            user_client=user_client,
            token_class=SlidingToken
        )
        optional_payloads = {k: payload[k] for k in set(payload) - set(token.payload)}
        for k, v in optional_payloads.items():
            token[k] = v
        # write event sign in activity
        ActivityService.create_activity(
            user=user, action=ActivityService.action_sign_in()
        )

        # PS-906
        # Check that the timestamp in the "refresh_exp" claim has not
        # passed
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)

        # Update the "exp" and "iat" claims
        token.set_exp()
        token.set_iat()
        return {"token": str(token)}


#  Custom login serializer
class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        email = attrs.get("email").lower()
        user = User.objects.filter(email=email).first()
        if user is not None and UserService.is_activated(user) is False:
            raise LoginWithoutVerificationException()
        return super(CustomLoginSerializer, self).validate(attrs)


class UpdateRoleUserClientSerializer(serializers.ModelSerializer):
    role_update = serializers.CharField(write_only=True)

    class Meta:
        model = UserClient
        fields = (
            "id",
            "status",
            "role",
            "user",
            "created",
            "role_update",
        )
        extra_kwargs = {
            "role": {
                "read_only": True,
            },
            "user": {
                "read_only": True,
            },
        }

    def validate_role_update(self, role_update):
        list_role_name = [i.lower() for i in role_name]
        if role_update not in list_role_name:
            raise serializers.ValidationError("Role name is invalid")
        return role_update

    def update(self, instance, validated_data):
        user = self.context.get("request").user
        organization_user = OrganizationService.query_set_member_organization(
            organization=instance.client.organization, user=user
        ).first()
        if (
                instance.role == RoleService.role_owner()
                and organization_user
                and organization_user.role.key
                not in OrganizationRoleActionService.get_role_action_with_all_organization()
        ):
            raise OwnerRoleUpdateException()

        # @TODO: Recheck if this is necessary
        role = Role.objects.get(key=validated_data.upper())
        instance.role = role
        instance.save()
        data = {"Role": role.name}
        ActivityService.create_activity(user=self.context.get('request').user,
                                        action=ActivityService.action_update_member(), data=data)
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    extra_message = (
        serializers.SerializerMethodField()
    )  # method below: get_extra_message

    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "extra_message",
            "is_seen",
            "status",
            "meta",
            "created",
        )

    def get_extra_message(self, obj):
        message_factory_instance = NotificationMessageFactory.get_message_instance(
            obj.type, obj
        )
        message = message_factory_instance.message_generator()
        return message


class OrganizationUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    delete_option = serializers.ChoiceField(
        ("DELETE_ALL", "DELETE_AND_KEEP_IN_WS"), write_only=True, required=False
    )

    class Meta:
        model = OrganizationUser
        fields = (
            "id",
            "role",
            "user",
            "status",
            "last_active",
            "created",
            "delete_option",
        )


class UpdateRoleUserOrganizationSerializer(serializers.ModelSerializer):
    role_update = serializers.CharField(write_only=True)

    class Meta:
        model = OrganizationUser
        fields = (
            "id",
            "status",
            "role",
            "user",
            "created",
            "role_update",
        )
        extra_kwargs = {
            "role": {
                "read_only": True,
            },
            "user": {
                "read_only": True,
            },
        }

    def validate_role_update(self, role_update):
        list_role_name = [i.upper() for i in role_name]
        if role_update.upper() not in list_role_name:
            raise serializers.ValidationError("Role name is invalid")
        return role_update

    def update(self, instance, validated_data):
        """
        update member's role in the ORGANIZATION
        role's changes effect:
            -> ADMIN, OWNER
                * grant permission for user to all clients in the ORGANIZATION
            -> STAFF, EXTERNAL_USER
                * just change the role
                * ignore user permissions from clients in the ORGANIZATION before changes
        """
        role = Role.objects.get(key=validated_data.get("role_update").upper())
        instance.role = role
        instance.save()
        if instance.role.key in OrganizationRoleActionService.get_role_action_with_all_organization():
            publisher.notify(
                event_type="UPDATE_ORG_MEMBER_ROLE",
                user_id=instance.user.user_id,
                organization_id=instance.organization_id,
                role_key=validated_data.get("role_update").upper()
            )
        # Log update member activity
        log_activity_task.delay(user_id=self.context.get('request').user.pk,
                                action=ActivityService.action_update_member(), data={"Role": role.name})
        return instance


class OrganizationInvitationSerializer(InvitationSerializer):
    MESSAGE_RAISE_EXIST_MANAGER = "This user already exists"
    MESSAGE_RAISE_EXIST_CLIENT = "This user already exists as an external user. Please check the external users page"

    def validate_email(self, email):
        email = email.lower()
        user = User.objects.filter(email=email).first()
        organization = self.context.get("organization")
        user_organization = OrganizationService.query_set_member_organization(
            user=user, organization=organization
        ).first()
        if user and user_organization:
            client_role = user_organization.role.key in [
                OrganizationRoleActionService.get_key_client()
            ]
            message = (
                self.MESSAGE_RAISE_EXIST_CLIENT
                if client_role
                else self.MESSAGE_RAISE_EXIST_MANAGER
            )
            raise MemberExistsException(message=message)
        return email

    def adding_member(self, is_force_invitation: bool = False):
        organization = self.context.get("organization")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        if self.validated_data.get("role"):
            # optional data in body request
            # if true -> invite as role assigned
            role = Role.objects.get(key=self.validated_data.get("role").upper())

        else:
            # if false -> role staff is default
            role = RoleService.role_staff()
        org_user = OrganizationService.create_user_organization(
            organization=organization,
            user=user,
            role=role,
            is_force_invitation=is_force_invitation,
        )
        # MWM-1425: grant all access clients in ORG
        # Optimized by PS-867
        if (
                org_user.role.key
                in OrganizationRoleActionService.get_role_action_with_all_organization()
        ):
            publisher.notify(
                # grant permission for user to all clients in the ORGANIZATION
                event_type="UPDATE_ORG_MEMBER_ROLE",
                user_id=org_user.user_id,
                organization_id=org_user.organization_id,
                role_key=role.key
            )
        return org_user

    def send_invitation(self, url):
        app_name = self.context.get("app_name")
        app_name = LIST_APP_CONFIG_DICT.get(app_name)
        admin = self.context.get("admin")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        organization = self.context.get("organization")
        EmailService.send_invitation_member_organization(user, url, organization, admin, app_name)


class ForceOrganizationInvitationSerializer(OrganizationInvitationSerializer):
    password = serializers.CharField()
    activation_link_template = None  # bypass inheritance
    web_base_url = serializers.CharField(validators=[validate_web_base_url])

    def create_for_non_exist_user(self):
        # override
        data = self.get_cleaned_data()
        password = self.validated_data.get("password")
        data.update({"password1": password, "password2": password})
        create_user_serializer = CustomRegisterSerializer(
            data=data, context=self.context_for_invitation
        )
        create_user_serializer.is_valid(raise_exception=True)
        create_user_serializer.save(self.context.get("request"))
        email = self.validated_data.get("email")
        verify_email_for_force_invitation = EmailAddress.objects.get(email=email)
        verify_email_for_force_invitation.verified = True
        verify_email_for_force_invitation.save()

    def send_force_invite_notification(self, user_existed: bool):
        app_name = self.context.get("app_name")
        app_name = LIST_APP_CONFIG_DICT.get(app_name)
        admin = self.context.get("admin")
        user = User.objects.filter(email=self.validated_data.get("email")).first()
        organization = self.context.get("organization")
        web_base_url = self.validated_data.get("web_base_url")
        password = self.validated_data.get("password")
        EmailService.send_force_invite_notification_member_organization(
            user, password, organization, admin, web_base_url, user_existed, app_name
        )


class OrganizationResendInvitationSerializer(serializers.Serializer):
    activation_link_template = serializers.CharField()


class OrganizationValidateTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)

    class Meta:
        model = OrganizationUser
        fields = "__all__"
        extra_kwargs = {
            "organization": {"read_only": True},
            "user": {"read_only": True},
            "role": {"read_only": True},
        }

    def add_member(self, user, organization):
        organization_user = OrganizationUser.objects.filter(
            user=user, organization=organization
        ).first()
        organization_user.pending_to_member()
        return organization_user

    def create(self, validated_data):
        token = self.validated_data.get("token")
        user, organization, inviter = OrganizationService.validate_token_invitation(token=token)
        with transaction.atomic():  # rollback it something makes db be not unique
            user_organization = self.add_member(user, organization)
            accepting_invitation_organization_signal.send(
                self.__class__,
                user_id=user.pk,
                organization_id=str(organization.pk),
                token=self.validated_data.get("token"),
            )
            UserService.activation(user)
            # log add member activity after user activation
            data = {"Full name": f"{user.first_name} {user.last_name}", "Email": user.email}
            log_activity_task.delay(user_id=inviter.pk if inviter else None, action=ActivityService.action_add_member(),
                                    data=data)
            if (
                    user_organization.role.key
                    in OrganizationRoleActionService.get_role_action_with_all_organization()
            ):
                publisher.notify(
                    # grant permission for user to all clients in the ORGANIZATION
                    event_type="UPDATE_ORG_MEMBER_ROLE",
                    user_id=user_organization.user_id,
                    organization_id=user_organization.organization_id,
                    role_key=user_organization.role.key
                )
        return user_organization

    def is_needed_changing_password(self, user):
        return UserService.is_needed_changing_password(user)


class OrganizationClientSerializer(ClientSerializer):
    has_access = serializers.SerializerMethodField()
    has_access_with_role = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + (
            "active",
            "has_access",
            "has_access_with_role",
            "owner",
        )
        extra_kwargs = {
            "logo": {"required": False},
            "active": {"required": False},
            "has_access": {"readonly": False},
            "has_access_with_role": {"readonly": False},
        }

    @property
    def get_user_request(self):
        user_request = self.context.get("user_request", None)
        if user_request:
            return user_request
        request = self.context.get("request")
        return request.user if request else None

    def get_owner(self, obj):
        return UserSerializer(obj.owner).data

    def get_has_access(self, instance):
        return OrganizationRoleService.get_query_set_user_client_access(
            client=instance,
            organization=instance.organization,
            user=self.get_user_request,
        ).exists()

    def get_has_access_with_role(self, instance):
        query_set = OrganizationRoleService.get_query_set_role_user(
            organization=instance.organization, user=self.get_user_request
        )
        if not query_set.exists():
            return None
        return query_set.first().role.key

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        organization = self.context.get("organization")
        # PS-587: Validate unique name of Client
        ClientService.unique_name_client(
            name=validated_data["name"], organization=organization
        )
        role_user = OrganizationRoleService.get_query_set_role_user(
            organization=organization, user=user
        ).first()
        active = (
            False
            if role_user.role.key == OrganizationRoleActionService.get_key_staff()
            else True
        )
        self.active = active
        validated_data["active"] = active
        with transaction.atomic():  # rollback it something makes db be not unique
            # DC-488: Normalize name client soft delete of organization
            ClientService.normalize_name_client_soft_delete_organization(
                name=validated_data["name"], organization=organization
            )
            # create client
            client = ClientService.create_client(
                owner=user, organization=organization, **validated_data
            )

            _app_profiles = get_app_name_profile()
            # observer pattern
            # make creating Workspace simple
            data = {
                "client_id": client.id,
                "app": _app_profiles,
                "organization_id": organization.id,
                "user_id": user.user_id,
            }
            publisher.notify("CREATE_WORKSPACE", **data)

        return client


class OrganizationAccessClientSerializer(serializers.Serializer):
    client_ids = serializers.ListField(allow_empty=False, child=serializers.UUIDField())
    has_access = serializers.BooleanField(default=True)


class UserInfoOrganizationClientSerializer(serializers.Serializer):
    organization = OrganizationSerializer
    clients = OrganizationClientSerializer(many=True)


class AppJSONWebTokenSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    @property
    def app_name_field(self):
        return "app"

    def validate_app(self, app):
        if app and app not in APP_NAME_BUILD_PROFILE:
            raise InvalidFormatException(mess="Field 'app' invalid!")
        return app

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.fields[self.app_name_field] = serializers.CharField()

    @property
    def exclude_attrs(self):
        return ["email", "password"]

    def validate(self, attrs):
        data = super().validate(attrs)
        # remove email and name
        exclude_fields = self.exclude_attrs
        for item in exclude_fields:
            del attrs[item]
        refresh = custom_token_handler(self.user, **dict(attrs))

        # data["refresh"] = str(refresh)
        # data["access"] = str(refresh.access_token)
        data["token"] = str(refresh)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        # update last login
        auth_signal.user_logged_in.send(
            sender=self.user.__class__,
            request=self.context.get("request", None),
            user=self.user,
        )
        # write event sign in activity
        attrs_activity = {"app_profile": attrs["app"]}
        ActivityService.create_activity(
            user=self.user, action=ActivityService.action_sign_in(), data=attrs_activity
        )
        if UserService.is_activated(user=self.user) is False:
            raise RegisteredWithoutVerificationException()

        return data


class OrganizationClientsModulesSerializer(OrganizationClientSerializer):
    modules = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta(OrganizationClientSerializer.Meta):
        fields = OrganizationClientSerializer.Meta.fields + ("modules", "role")

    def get_modules(self, obj):
        return ClientModuleService.get_client_modules_detail(client=obj)

    def get_role(self, obj):
        user = self.context.get("request", None).user
        client_user = ClientService.query_set_member_client(
            client=obj, user=user
        ).first()
        return RoleSerializer(client_user.role).data


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Activity


class ActivityObjectSerializer(ActivitySerializer):
    user = UserSerializer()
    object_type = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "user",
            "action",
            "action_label",
            "object_id",
            "object_type",
            "data",
            "created",
        )
        model = Activity

    def get_object_type(self, activity):
        return (
            ContentType.objects.get_for_model(activity.object).name
            if activity.object
            else None
        )

    def get_action_label(self, activity):
        return dict(ACTION_ACTIVITY)[activity.action]


class ActivityActionSerializer(ActivityObjectSerializer):
    data = serializers.JSONField(required=False, default={})
    action = serializers.ChoiceField(choices=ACTION_ACTIVITY)
    object_id = serializers.UUIDField(required=True)
    object_type = serializers.ChoiceField(
        required=True, choices=(("organization", "client"))
    )

    class Meta(ActivityObjectSerializer.Meta):
        fields = (
            "action",
            "object_id",
            "object_type",
            "data",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created": {"read_only": True},
        }


class AppClientConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppClientConfig
        fields = "__all__"
        extra_kwargs = {"created": {"read_only": True}, "updated": {"read_only": True}}


class AppClientConfigSwitcherSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(default=True)


# Client Module Info Internal
class ClientInfoInternalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "logo",
            "active",
        )


class ClientModulesInternalSerializer(ClientModulesSerializer):
    class Meta(ClientModulesSerializer.Meta):
        fields = (
            "module",
            "enabled",
        )


class OrganizationInternalSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Organization
        fields = "__all__"


class ClientStatusInfoInternalSerializer(ClientInfoInternalSerializer):
    organization = OrganizationInternalSerializer()
    owner = UserSerializer()

    class Meta(ClientInfoInternalSerializer.Meta):
        fields = "__all__"
