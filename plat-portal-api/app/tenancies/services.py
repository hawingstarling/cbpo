from typing import Any, List

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.template.loader import render_to_string
from itsdangerous import URLSafeTimedSerializer
from rest_framework.authtoken.models import Token

from app.core.logger import logger
from app.core.services.app_confg import AppService
from app.core.utils import *  # noqa
from app.tenancies.exceptions.organization import UniqueClientOrganizationException
from config.settings.common import DJANGO_DEFAULT_FROM_EMAIL, SECRET_KEY
from .config_static_variable import (
    DAYS_EXPIRED,
    MEMBER_STATUS,
    TYPE_NOTIFICATION,
    role_name,
)
from .exceptions.organization import AccessClientException
from .models import (
    AppClientConfig,
    Client,
    ClientModule,
    Notification,
    Organization,
    OrganizationUser,
    Role,
    User,
    UserClient,
    UserOTP,
    ValidateToken,
)
from app.tenancies.tasks import log_activity_task
from .activity_services import ActivityService

TEAM_NAME = settings.TEAM_NAME
APP_NAME = settings.APP_NAME


class EmailService:
    @staticmethod
    def validate_new_email(email):
        user = User.objects.filter(email=email).first()
        if user:
            return False
        return True

    @staticmethod
    def send_email(subject, msg_html, recipient_list):
        email_from = DJANGO_DEFAULT_FROM_EMAIL
        msg = EmailMessage(
            subject=subject, body=msg_html, from_email=email_from, to=recipient_list
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    @staticmethod
    def send_code_reset_password(user, code):
        subject = "Verification code for password recovery at %s" % APP_NAME
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "code": code,
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
        }
        msg_html = render_to_string("password/reset_password.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_code_changing_email(user, code):
        subject = "Change email verification code at %s" % APP_NAME
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "code": code,
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
        }
        msg_html = render_to_string("email/changing_email.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_change_email_successfully(user, new_email):
        subject = "Email changed successfully at %s" % APP_NAME
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
            "new_email": new_email,
        }
        msg_html = render_to_string("email/send_change_email_successfully.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_code_activation_user(user, code):
        subject = "Activate your %s Account" % APP_NAME
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "code": code,
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
        }
        msg_html = render_to_string("registration/activation.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_invitation_member_client(user, url, client, admin, app_name=APP_NAME):
        subject = "Join your team on %s" % app_name
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "url": url,
            "subject": subject,
            "client_name": client.name,
            "sender_name": UserService.get_role_label_in_email(admin, role="sender"),
            "app_name": app_name,
            "team_name": TEAM_NAME,
            "expired_days": DAYS_EXPIRED,
        }
        msg_html = render_to_string("registration/invitation_client.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_force_invite_notification_member_client(
            user: User,
            password: str,
            client: Client,
            admin: User,
            web_base_url: str,
            user_existed: bool,
            app_name=APP_NAME,
    ):
        subject = "Join your team on %s" % app_name
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "url": web_base_url,
            "subject": subject,
            "client_name": client.name,
            "sender_name": UserService.get_role_label_in_email(admin, role="sender"),
            "app_name": app_name,
            "team_name": TEAM_NAME,
            "user_email": user.email,
            "password": password,
            "user_existed": user_existed,
        }
        msg_html = render_to_string(
            "registration/force_invitation_notice_client.html", data
        )
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_invitation_member_organization(
            user: User, url: str, organization: Organization, admin: User, app_name: APP_NAME,
    ):
        subject = "Join your team on %s" % app_name
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "url": url,
            "subject": subject,
            "org_name": organization.name,
            "sender_name": UserService.get_role_label_in_email(admin, role="sender"),
            "app_name": app_name,
            "team_name": TEAM_NAME,
            "expired_days": DAYS_EXPIRED,
        }
        msg_html = render_to_string("registration/invitation_organization.html", data)
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_force_invite_notification_member_organization(
            user: User,
            password: str,
            organization: Organization,
            admin: User,
            web_base_url: str,
            user_existed: bool,
            app_name: APP_NAME,
    ):
        subject = "Join your team on %s" % app_name
        data = {
            "receiver_name": UserService.get_role_label_in_email(user, role="receiver"),
            "url": web_base_url,
            "subject": subject,
            "org_name": organization.name,
            "sender_name": UserService.get_role_label_in_email(admin, role="sender"),
            "app_name": app_name,
            "team_name": TEAM_NAME,
            "user_email": user.email,
            "password": password,
            "user_existed": user_existed,
        }
        msg_html = render_to_string(
            "registration/force_invitation_notice_organization.html", data
        )
        EmailService.send_email(subject, msg_html, [user.email])

    @staticmethod
    def send_approve_active_client_email(
            user_create: User,
            users_approve: List[User],
            client: Client,
            organization: Organization,
    ):
        subject = "New workspace is waiting for your approval on %s" % APP_NAME
        data = {
            "receiver_name": "owner",
            "user_email_create": user_create.email,
            "client_name": client.name,
            "organization_name": organization.name,
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
        }
        msg_html = render_to_string("email/send_approve_active_client.html", data)
        list_email_receive = [user.email for user in users_approve]
        EmailService.send_email(subject, msg_html, list_email_receive)

    @staticmethod
    def send_notify_lwa_setting(app_lwa_id: str, app_lwa_name: str, date_expired: str, url_django_admin: str,
                                emails: List[str]):
        subject = f"{app_lwa_name} LWA Credentials Expiry Reminder"
        data = {
            "receiver_name": f"{TEAM_NAME} Administrator",
            "app_lwa_id": app_lwa_id,
            "app_lwa_name": app_lwa_name,
            "date_expired": date_expired,
            "url_django_admin": url_django_admin,
            "subject": subject,
            "app_name": APP_NAME,
            "team_name": TEAM_NAME,
        }
        msg_html = render_to_string("app_setting/notify_lwa_setting.html", data)
        EmailService.send_email(subject, msg_html, emails)


class UserService:
    @staticmethod
    def create_user(email, password):
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def create_token(user):
        token = Token.objects.create(user=user)
        token.save()
        return token

    @staticmethod
    def token_exist(user):
        return Token.objects.filter(user=user).exists()

    @staticmethod
    def change_password(user, password):
        with transaction.atomic():
            user.set_password(password)
            user.save()
            user_otp = UserOTP.objects.filter(user=user).first()
            if user_otp:
                user_otp.reset_after_verified()
        return user

    @staticmethod
    def activation(user):
        email_address = EmailAddress.objects.filter(user=user).first()
        email_address.verified = True
        email_address.save()

    @staticmethod
    def change_email_address(user, new_email):
        email_address = EmailAddress.objects.filter(user=user).first()
        email_address.email = new_email
        email_address.verified = True
        email_address.save()

    @staticmethod
    def is_activated(user):
        email_address = EmailAddress.objects.filter(user=user).first()
        if email_address.verified is True:
            return True
        return False

    @staticmethod
    def is_needed_changing_password(user):
        #  verified by last login
        if user.last_login is not None:
            return False
        return True

    @staticmethod
    def get_role_label_in_email(user, role="sender"):
        if role == "sender":
            return user.first_name if user.first_name else user.email
        # else be receiver
        return user.first_name if user.first_name else "there"


class ClientService:
    @staticmethod
    def get_queryset_client(user: User = None, **kwargs):
        queryset = Client.objects.all()
        if user:
            queryset = queryset.filter(userclient__user=user)
        if kwargs:
            queryset = queryset.filter(**kwargs)
        return queryset

    @staticmethod
    def create_client(owner, **validated_data):
        client = Client.objects.create(owner=owner, **validated_data)
        return client

    @staticmethod
    def validate_user_exist_in_client(user, client):
        user_client = UserClient.objects.filter(user=user, client=client).first()
        if user_client:
            if user_client.is_pending() is False:
                return True
        return False

    @staticmethod
    def validate_token_invitation(token):
        try:
            user_id, client_id, inviter_id = ValidateToken.validate_token_invitation_client(token)
            #
            user = User.objects.filter(pk=user_id).first()
            inviter = User.objects.filter(pk=inviter_id).first()
            client = Client.objects.filter(pk=client_id).first()
            if (
                    not user
                    or not client
                    or not UserClient.objects.filter(client=client, user=user).exists()
            ):
                raise InvalidTokenException()
            return user, client, inviter
        except Exception:
            raise InvalidTokenException("Token is expired!")

    @staticmethod
    def generate_token_invitation(
            user, client, expired_seconds=60 * 60 * 24 * DAYS_EXPIRED, inviter: User = None
    ):
        try:
            s = URLSafeTimedSerializer(SECRET_KEY)
            token_data = {"user_id": str(user.pk), "client_id": str(client.pk)}
            if inviter:
                token_data["inviter_id"] = str(inviter.pk)
            token = s.dumps(token_data)
            return token
        except Exception as ex:
            print(ex)
            return None

    @staticmethod
    def query_set_member_client(client: Client = None, user: User = None, **kwargs):
        client_user = UserClient.objects.all()
        if client:
            client_user = UserClient.objects.filter(client=client)
        if user:
            client_user = client_user.filter(user=user)
        if kwargs:
            client_user = client_user.filter(**kwargs)
        return client_user

    @staticmethod
    def get_status_invitation(token: str = None):
        status = None
        verify = False
        is_change_password = False
        if not token or not isinstance(token, str):
            return status, verify, is_change_password
        user, client, inviter = ClientService.validate_token_invitation(token=token)
        user_client = ClientService.query_set_member_client(
            client=client, user=user, status=MEMBER_STATUS[0][0]
        )
        if user:
            is_change_password = UserService.is_needed_changing_password(user=user)
        if user_client.exists():
            verify = True
            status = "Accept"
            # log add member activity
            data = {"Full name": f"{user.first_name} {user.last_name}", "Email": user.email}
            log_activity_task.delay(user_id=inviter.pk if inviter else None, action=ActivityService.action_add_member(),
                                    data=data)

        notification = (
            Notification.objects.filter(
                type=TYPE_NOTIFICATION[0][0],
                object_id=client.pk,
                object_type=ContentType.objects.get_for_model(client),
                user=user,
            )
            .order_by("-created")
            .first()
        )
        action = notification.meta.get("action", None) if notification else None
        if not verify and action and action in ["Decline"]:
            verify = True
            status = "Decline"
        return verify, status, is_change_password

    @staticmethod
    def unique_name_client(
            name: str = None, organization: Organization = None, client: Client = None
    ):
        """
        Unique Client Organization Exception
        :param name:
        :param organization:
        :param client:
        :return:
        """
        # All objects if unique for update else we should be using objects for check creating
        model_instance = Client.objects if client is None else Client.all_objects
        obj = model_instance.filter(name__iexact=name, organization=organization)
        validate = obj.exists() and (
                not client
                or obj.first().pk != client.pk
                or (obj.first().pk == client.pk and name.lower() != client.name.lower())
        )
        if validate:
            raise UniqueClientOrganizationException()

    @staticmethod
    def normalize_name_client_soft_delete_organization(
            name: str = None, organization: Organization = None
    ):
        """
        Normalize name client of organization when create same name record soft delete
            1. Find name client same with name Client Soft Delete Model of Organization ( using manage all_objects of client)
            2. If find_client = True change name find_client with format = name + '-' +  now()
        :param name:
        :param organization:
        :return:
        """
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filter = {"name__iexact": name, "organization_id": str(organization.pk)}
        find = SoftDeleteModelCheck.get_soft_delete_model(model=Client, **filter)
        if find and find.is_removed:
            normalize_name = "{name}-{time}".format(name=find.name, time=time)
            find.name = normalize_name
            find.save()


class RoleService:
    @staticmethod
    def role_admin():
        role = Role.objects.filter(key="ADMIN").first()
        return role

    @staticmethod
    def role_staff():
        role = Role.objects.filter(key="STAFF").first()
        return role

    @staticmethod
    def role_owner():
        role = Role.objects.filter(key="OWNER").first()
        return role

    @staticmethod
    def role_client():
        role = Role.objects.filter(key="CLIENT").first()
        return role

    @staticmethod
    def validate_role_name(role: str = None):
        if not role:
            return False
        list_role_name = [i.lower() for i in role_name]
        if role not in list_role_name:
            return False
        return True


class SoftDeleteModelCheck:
    @staticmethod
    def get_soft_delete_model(model, **kwargs):
        # return instance if it is soft deleted
        # all_objects is defined for for accessing soft deleted instances
        return model.all_objects.filter(**kwargs).first()

    @staticmethod
    def get_soft_delete_list(model, **kwargs):
        # return instance if it is soft deleted
        # all_objects is defined for for accessing soft deleted instances
        return model.all_objects.filter(**kwargs).all()

    @staticmethod
    def revert_update_soft_delete_model(model, conditions, **kwargs):
        record = SoftDeleteModelCheck.get_soft_delete_model(model=model, **conditions)
        if record:
            model.all_objects.filter(pk=str(record.pk)).update(**kwargs)
            return True
        return False


class UserClientService:
    @staticmethod
    def create_user_client(
            client,
            user,
            role,
            status: str = MEMBER_STATUS[1][0],
            invite: bool = False,
            is_force_invitation: bool = False,
    ):
        """
        Create user client when create client or invite user to client.
        @param client:
        @param user:
        @param role:
        @param status:
        @param invite:
        @param is_force_invitation:
        @return:
        """
        if (role == RoleService.role_owner() and not invite) or is_force_invitation:
            _status = MEMBER_STATUS[0][0]
        else:
            _status = status

        filter_dict = {"user": user, "client": client}
        user_client = SoftDeleteModelCheck.get_soft_delete_model(
            UserClient, **filter_dict
        )

        if user_client is not None:
            # instance is soft deleted, switch is_removed status
            user_client.is_removed = False
            user_client.status = _status
            user_client.role = role
            user_client.save()
            return user_client

        user_client, _ = UserClient.objects.update_or_create(
            client=client, user=user, role=role, defaults={"status": _status}
        )
        return user_client

    @staticmethod
    def validate_role_admin_or_manager(user, client):
        user_client = UserClient.objects.filter(user=user, client=client).first()
        organization_user = OrganizationService.validate_role_user_organization(
            organization=client.organization,
            user=user,
            roles=OrganizationRoleActionService.get_role_action_with_all_organization(),
        )
        if organization_user:
            return True
        if user_client:
            return user_client.is_admin_or_manager()
        return False

    @staticmethod
    def validate_member_in_client(user, client):
        user_client = UserClient.objects.filter(
            user=user, client=client, client__active=True
        ).first()
        organization_user = OrganizationService.validate_role_user_organization(
            organization=client.organization,
            user=user,
            roles=OrganizationRoleActionService.get_role_action_with_all_organization(),
        )
        if user_client or organization_user:
            return True
        return False

    @staticmethod
    def adding_notification_model(noti_type, client, user, meta, author):
        notification = Notification.objects.create(
            type=noti_type,
            object_id=client.pk,
            object_type=ContentType.objects.get_for_model(client),
            user=user,
            meta=meta,
            author=author,
        )
        notification.save()

    @staticmethod
    def get_query_set_access_of_user(
            organization: Organization,
            user: User,
            status: str = MEMBER_STATUS[0][0],
            **kwargs,
    ):
        module_app_profile = get_modules_app_profile()
        queryset = Client.objects.filter(
            userclient__user=user,
            userclient__is_removed=False,
            userclient__status=status,
        )
        if organization:
            queryset = queryset.filter(organization=organization)
        if module_app_profile:
            queryset = queryset.filter(
                clientmodule__module__in=module_app_profile
            ).distinct()
        if kwargs:
            queryset = queryset.filter(**kwargs)
        return queryset


class ClientModuleService:
    @staticmethod
    def get_query_set_client_module(client: Client = None, **kwargs):
        queryset = ClientModule.objects.all()
        if client:
            queryset = queryset.filter(client=client)
        if kwargs:
            queryset = queryset.filter(**kwargs)
        return queryset

    @staticmethod
    def create_client_module(
            client: Client = None, enabled: bool = False, app_name: str = None
    ):
        modules = (
            AppService().get_modules_app(app_name=app_name)
            if app_name
            else AppService().get_all_modules_app()
        )
        for module in modules:
            # find all include record soft delete and revert module
            update_dict = {"is_removed": False, "enabled": enabled}
            if SoftDeleteModelCheck.revert_update_soft_delete_model(
                    model=ClientModule,
                    conditions={"client": client, "module": module},
                    **update_dict,
            ):
                continue
            ClientModule.objects.create(client=client, module=module, enabled=enabled)

    @staticmethod
    def get_organizations_clients_modules_detail(
            organizations: List[Organization] = [], **kwargs
    ):
        if not organizations or not kwargs:
            return None
        queryset = ClientModule.objects.filter(client__organization__in=organizations)
        if kwargs:
            queryset = queryset.filter(**kwargs)
        data = {}
        for item in queryset.iterator():
            client_id = str(item.client.pk)
            temp = data[client_id] if item.client.pk in data else []
            temp_data = {
                "id": str(item.pk),
                "module": item.module,
                "enabled": item.enabled,
            }
            temp.append(temp_data)
            data[client_id] = temp
        return data

    @staticmethod
    def get_client_modules_detail(client: Client = None, **kwargs):
        queryset = ClientModule.objects.filter(module__in=get_modules_app_profile())
        if client:
            queryset = queryset.filter(client=client)
        if kwargs:
            queryset = queryset.filter(**kwargs)
        data = []
        for item in queryset.iterator():
            temp_data = {
                "id": str(item.pk),
                "module": item.module,
                "enabled": item.enabled,
            }
            data.append(temp_data)
        return data


class UserOTPService:
    @staticmethod
    def get_or_create_code(user):
        obj, created = UserOTP.objects.get_or_create(user=user)
        obj.reset_code()
        obj.count += 1
        obj.verified = False
        obj.save()
        return obj.get_code

    @staticmethod
    def get_token(user):
        user_otp = UserOTP.objects.filter(user=user).first()
        return user_otp.get_token

    @staticmethod
    def validate_user_code(user, code):
        return UserOTP.objects.filter(user=user).first().matching_code(input_code=code)

    @staticmethod
    def verify_used_code(user):
        return UserOTP.objects.filter(user=user).first().get_verified_code

    @staticmethod
    def reset_after_verified(user):
        UserOTP.objects.filter(user=user).first().reset_after_verified()

    @staticmethod
    def validate_token_otp(token):
        return ValidateToken.validate_token_otp(token)


class LastModificationServices:
    @staticmethod
    def get_modified_field(list_objs):
        #  get the last modification time
        res = [i.modified for i in list_objs]
        return res

    @staticmethod
    def client_modules(client):
        list_modules = ClientModule.objects.filter(client=client).all()
        return LastModificationServices.get_modified_field(list_modules)


class OrganizationService:
    @staticmethod
    def query_set_member_organization_empty():
        return OrganizationUser.objects.none()

    @staticmethod
    def query_set_client_organization(
            organization: Organization = None,
            role: Role = None,
            user: User = None,
            status: str = "all",
            **kwargs,
    ):
        """
        Make query set get client of organization
            1. default get all client of organization
            2. if role:
                a. Role OWNER | ADMIN get all client include client active vs pending ,
                                    syntax lookup = lookup | Q(active=False)
                b. Role not in OWNER | ADMIN get client user is granted that client and client user is owner with status pending ,
                                    syntax lookup = lookup | Q(active=False,owner=user)
            4. mixed filter from **kwargs
        :param organization:
        :param role:
        :param user:
        :param status:
        :param app_profile:
        :param kwargs:
        :return:
        """
        query_set = Client.objects.filter(organization=organization)
        lookup = None
        # query set with role of user Organization User
        if role:
            if role.key not in ["OWNER", "ADMIN"]:
                condition_enabled = Q(
                    active=True, userclient__user=user, userclient__is_removed=False
                )
                args = {
                    "all": condition_enabled | Q(active=False, owner=user),
                    "enabled": condition_enabled,
                    "pending": Q(active=False, owner=user),
                }
                lookup = args.get(status)
            else:
                condition_enabled = Q(active=True)
                args = {
                    "all": condition_enabled | Q(active=False),
                    "enabled": condition_enabled,
                    "pending": Q(active=False),
                }
                lookup = args.get(status)
        if lookup:
            query_set = query_set.filter(lookup)
        if kwargs:
            query_set = query_set.filter(**kwargs)
        return query_set

    @staticmethod
    def query_set_member_organization(
            organization: Organization = None, user: User = None, **kwargs
    ):
        if not organization:
            return OrganizationUser.objects.none()
        organization_user = OrganizationUser.objects.filter(organization=organization)
        if user:
            organization_user = organization_user.filter(user=user)
        if kwargs:
            organization_user = organization_user.filter(**kwargs)
        return organization_user

    @staticmethod
    def validate_role_user_organization(
            user: User = None, organization: Organization = None, roles=[]
    ):
        if not user or not organization:
            return False
        query_set = OrganizationUser.objects.filter(
            organization=organization, user=user, status=MEMBER_STATUS[0][0]
        )
        if roles:
            query_set = query_set.filter(role__key__in=roles)
        return query_set.exists()

    @staticmethod
    def create_organization(owner: User, **validated_data):
        organization, created = Organization.objects.get_or_create(
            owner=owner, **validated_data
        )
        return organization

    @staticmethod
    def get_organizations(user: User = None, **kwargs):
        query_set = Organization.objects.all()
        if user:
            lookup = (
                    Q(
                        organizationuser__user=user,
                        organizationuser__status=MEMBER_STATUS[0][0],
                        organizationuser__is_removed=False,
                    )
                    | Q(owner=user)
            )
            query_set = Organization.objects.filter(lookup)
        if kwargs:
            query_set = query_set.filter(**kwargs)
        return query_set

    @staticmethod
    def create_user_organization(
            user: User,
            organization: Organization,
            role: Role,
            status: str = MEMBER_STATUS[1][0],
            is_force_invitation: bool = False,
    ):
        _status = MEMBER_STATUS[0][0] if is_force_invitation else status

        filter_dict = {"user": user, "organization": organization}
        user_organization = SoftDeleteModelCheck.get_soft_delete_model(
            OrganizationUser, **filter_dict
        )

        if user_organization is not None:
            # instance is soft deleted, switch is_removed status
            user_organization.is_removed = False
            user_organization.status = _status
            user_organization.role = role
            user_organization.save()
            return user_organization

        user_organization, _ = OrganizationUser.objects.get_or_create(
            organization_id=organization.pk,
            user_id=user.pk,
            role_id=role.pk,
            status=_status,
        )
        return user_organization

    @staticmethod
    def generate_token_invitation(
            user: User,
            organization: Organization,
            expired_seconds=60 * 60 * 24 * DAYS_EXPIRED,
            inviter: User = None
    ):
        if not user or not organization:
            return None
        try:
            s = URLSafeTimedSerializer(SECRET_KEY)
            token_data = {
                "user_id": str(user.pk),
                "organization_id": str(organization.pk)
            }
            if inviter:
                token_data["inviter_id"] = str(inviter.pk)
            token = s.dumps(token_data)
            return token
        except Exception as ex:
            print(ex)
            return None

    @staticmethod
    def create_user_module_permission(user: User, organization: Organization):
        pass

    @staticmethod
    def adding_notificaiton_model(
            noti_type: str, organization: Organization, user: User, meta: dict, author: User
    ):
        notification = Notification.objects.create(
            type=noti_type,
            object_id=organization.pk,
            object_type=ContentType.objects.get_for_model(organization),
            user=user,
            meta=meta,
            author=author,
        )
        notification.save()

    @staticmethod
    def validate_token_invitation(token):
        user_id, organization_id, inviter_id = ValidateToken.validate_token_invitation_organization(
            token
        )
        #
        user = User.objects.filter(pk=user_id).first()
        inviter = User.objects.filter(pk=inviter_id).first()
        organization = Organization.objects.filter(pk=organization_id).first()
        if (
                not user
                or not organization
                or not OrganizationUser.objects.filter(
            organization=organization, user=user
        ).exists()
        ):
            raise InvalidTokenException()
        return user, organization, inviter

    @staticmethod
    def grant_access_all_client_organization(
            clients: List[Client], users: List[User], role: Role = None
    ):
        if not role:
            role = RoleService.role_owner()
        for client in clients:
            OrganizationService.grant_access_client_organization(
                client=client, users=users, role=role
            )

    @staticmethod
    def grant_access_client_organization(
            client: Client, users: List[User], role: Role = None, **kwargs
    ):
        if not role:
            role = RoleService.role_owner()
        if not client.active:
            logger.error("Client {} must active".format(client.id))
            raise GenericException("Client must active")
        # create user client module
        client_modules = ClientModuleService.get_query_set_client_module(
            client=client, enabled=True
        )
        if not client_modules.exists():
            ClientModuleService.create_client_module(client=client, enabled=True)
        for user in users:
            # create user client
            user_client = UserClientService.create_user_client(
                client=client, user=user, role=role, status=MEMBER_STATUS[0][0]
            )
            # remove legacy permission
            # create user module permission
            # UserModulePermissionService.create_user_module_permission(
            #     client=client,
            #     user=user,
            #     role=role,
            #     user_client=user_client,
            #     enabled=True,
            # )
        # Activity grant access for user

    @staticmethod
    def queryset_list_users_organization(
            organization: Organization = None, roles: list = [], **kwargs
    ):
        queryset = User.objects.filter(
            organizationuser__organization=organization,
            organizationuser__role__key__in=roles,
        )
        if kwargs:
            queryset = queryset.filter(**kwargs)
        queryset = queryset.distinct()
        return queryset

    @staticmethod
    def approval_client_to_active(organization: Organization, client: Client) -> Any:
        if client.active:
            raise GenericException("Client have approval to active!")
        with transaction.atomic():
            client.active = True
            client.save()
            users_grant_permission = list(
                OrganizationService.queryset_list_users_organization(
                    organization=organization,
                    roles=OrganizationRoleActionService.get_role_action_with_all_organization(),
                    organizationuser__status=MEMBER_STATUS[0][0],
                ).all()
            )
            users_grant_permission.append(client.owner)
            OrganizationService.grant_access_client_organization(
                client=client, organization=organization, users=users_grant_permission
            )

    @staticmethod
    def add_invitation_notification(
            token: str = None,
            organization: Organization = None,
            user: User = None,
            author: User = None,
    ) -> Any:
        notification_type = TYPE_NOTIFICATION[0][0]  # ->Invitation
        meta = {
            "organization_id": str(organization.pk),
            "type": "organization",
            "invitation_token": token,
        }
        OrganizationService.adding_notificaiton_model(
            notification_type, organization, user, meta, author
        )

    @staticmethod
    def get_status_invitation(token: str = None):
        status = None
        verify = False
        is_change_password = False
        if not token or not isinstance(token, str):
            return status, verify, is_change_password
        user, organization, inviter = OrganizationService.validate_token_invitation(token=token)
        user_org = OrganizationService.query_set_member_organization(
            organization=organization, user=user, status=MEMBER_STATUS[0][0]
        )
        if user:
            is_change_password = UserService.is_needed_changing_password(user=user)
        if user_org.exists():
            verify = True
            status = "Accept"
            # log add member activity after accept invitation
            data = {"Full name": f"{user.first_name} {user.last_name}", "Email": user.email}
            log_activity_task.delay(user_id=inviter.pk if inviter else None, action=ActivityService.action_add_member(),
                                    data=data)

        notification = (
            Notification.objects.filter(
                type=TYPE_NOTIFICATION[0][0],
                object_id=organization.pk,
                object_type=ContentType.objects.get_for_model(organization),
                user=user,
            )
            .order_by("-created")
            .first()
        )
        action = notification.meta.get("action", None) if notification else None
        if not verify and action and action in ["Decline"]:
            verify = True
            status = "Decline"
        return verify, status, is_change_password

    @staticmethod
    def destroy_access_user_organization(
            organization: Organization = None, user: User = None
    ):
        with transaction.atomic():
            #
            ClientService.query_set_member_client(
                user=user, client__organization=organization
            ).delete()
            #
            OrganizationService.query_set_member_organization(
                organization=organization, user=user
            ).delete()

    @staticmethod
    def check_user_in_WS(organization: Organization, user: User):
        return ClientService.query_set_member_client(
            user=user, client__organization=organization
        ).count()

    @staticmethod
    def delete_org_user_only(organization: Organization, user: User):
        """[summary] delete org user and move it to external user
        -> change role user in ORG from member to CLIENT

        Args:
            organization (Organization): [description]
            user (User): [description]
        """
        OrganizationService.query_set_member_organization(
            organization=organization, user=user
        ).update(role=Role.objects.get(key="CLIENT"))

    @staticmethod
    def destroy_access_user_member_organization(
            organization: Organization = None, user: User = None
    ):
        user_organization = OrganizationService.query_set_member_organization(
            organization=organization, user=user
        ).first()
        if (
                user_organization
                and user_organization.role.key
                not in OrganizationRoleActionService.get_role_action_with_all_organization()
        ):
            with transaction.atomic():
                #
                client_user = ClientService.query_set_member_client(
                    user=user, client__organization=organization
                )
                if not client_user.exists():
                    #
                    OrganizationService.query_set_member_organization(
                        organization=organization, user=user
                    ).delete()


class OrganizationRoleActionService:
    @staticmethod
    def get_key_owner():
        return "OWNER"

    @staticmethod
    def get_key_admin():
        return "ADMIN"

    @staticmethod
    def get_key_staff():
        return "STAFF"

    @staticmethod
    def get_key_client():
        return "CLIENT"

    @staticmethod
    def get_role_action_with_all_organization():
        return ["OWNER", "ADMIN"]

    @staticmethod
    def get_role_create_client():
        return OrganizationRoleActionService.get_role_action_with_all_organization() + [
            "STAFF"
        ]

    @staticmethod
    def get_role_access_organization():
        return OrganizationRoleActionService.get_role_action_with_all_organization() + [
            "STAFF"
        ]


class OrganizationRoleService:
    @staticmethod
    def get_permission_access_organization(
            organization: Organization = None, user: User = None
    ) -> bool:
        user_organization = OrganizationRoleService.get_query_set_role_user(
            user=user, organization=organization
        ).first()
        if (
                not user_organization
                or user_organization.role.key
                not in OrganizationRoleActionService.get_role_access_organization()
        ):
            return False
        return True

    @staticmethod
    def get_query_set_user_client_access(
            organization: Organization, user: User, client: Client, **kwargs
    ) -> Any:
        # make lookup
        lookup = Q(client__organization=organization, is_removed=False) & (
                Q(client=client, user=user, status=MEMBER_STATUS[0][0])
                | Q(
            client__organization__organizationuser__user=user,
            client__organization__organizationuser__role__key__in=OrganizationRoleActionService.get_role_action_with_all_organization(),
        )
        )
        query_set = UserClient.objects.filter(lookup)
        if kwargs:
            query_set = query_set.filter(**kwargs)
        return query_set

    @staticmethod
    def get_query_set_role_user(
            organization: Organization = None, user: User = None, **kwargs
    ) -> Any:
        query_set = OrganizationUser.objects.filter(
            organization=organization, user=user
        )
        if kwargs:
            query_set = query_set.filter(**kwargs)
        return query_set

    @staticmethod
    def update_access_clients_for_user(
            organization: Organization,
            user: User,
            client_ids: list = [],
            access: bool = True,
            role: Role = None,
    ) -> Any:
        if not role:
            role = RoleService.role_staff()
        member_organization = OrganizationService.query_set_member_organization(
            organization=organization, user=user
        ).first()
        if member_organization and member_organization.role.key in ["OWNER"]:
            raise AccessClientException(message="Request to access invalid!")
        #
        if OrganizationService.query_set_client_organization(
                organization=organization, pk__in=client_ids
        ).count() < len(client_ids):
            raise AccessClientException(message="Client Ids request to access invalid!")
        try:
            with transaction.atomic():
                for client_id in client_ids:
                    client = Client.objects.get(pk=client_id)
                    if access:
                        OrganizationService.grant_access_client_organization(
                            client=client, role=role, users=[user]
                        )
                    else:
                        UserClient.objects.filter(client=client, user=user).delete()
        except Exception as ex:
            raise ex


class AppClientConfigService:
    @staticmethod
    def get_query_set_client_app_profile(client: Client = None, **kwargs) -> Any:
        query_set = AppClientConfig.objects.filter(client=client)
        if kwargs:
            query_set = query_set.filter(**kwargs)
        return query_set

    @staticmethod
    def create_client_app_profile(
            client: Client = None, app: str = None, enabled: bool = False, **kwargs
    ) -> Any:
        obj = AppClientConfig.objects.get_or_create(
            client=client, app=app, enabled=enabled, **kwargs
        )
        return obj

    @staticmethod
    def switching_client_app_profile(
            client: Client = None, app: str = None, enabled: bool = False
    ) -> Any:
        AppClientConfig.objects.update_or_create(
            client=client, app=app, defaults={"enabled": enabled}
        )

    @staticmethod
    def get_client_query_set_join_client_app_profile(
            queryset: QuerySet, app_profile: str = None
    ):
        # Join check config app client
        app_profile = get_app_name_profile() if not app_profile else app_profile
        query_set_client_access = queryset.filter(
            appclientconfig__app=app_profile, appclientconfig__enabled=True
        ).distinct()
        return query_set_client_access
