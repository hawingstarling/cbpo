import logging
import sys

from django import VERSION
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from app.tenancies.config_static_variable import NOTIFICATION_STATUS
from app.tenancies.mailchimp_services import add_member_mailchimp
from app.tenancies.models import (
    UserClient,
    Notification,
    OrganizationUser,
    User,
)
from app.tenancies.observer.publisher import publisher

django_command = sys.argv[1]
logger = logging.Logger("catch_all")


@receiver(post_save, sender=User)
def signal_user(**kwargs):
    if django_command == "test":
        return
    if not settings.MAILCHIMP_ENABLED:
        return
    is_new_user = kwargs.get("created", False)
    if is_new_user:
        instance = kwargs.get("instance")
        add_member_mailchimp(instance)


@receiver(post_save, sender=UserClient)
def automatic_permissions(sender, **kwargs):
    obj = kwargs.get("instance")

    if obj.is_removed is True:
        publisher.notify(
            event_type="DELETE_MEMBER",
            object_id=obj.id
        )
        return

    is_created = kwargs.get("created", False)

    if is_created:
        publisher.notify(
            event_type="CREATE_WORKSPACE_MEMBER",
            user_id=obj.user_id,
            organization_id=obj.client.organization_id,
            client_id=obj.client_id
        )
        return


@receiver(post_save, sender=OrganizationUser)
def automatic_permissions_org_user(sender, **kwargs):
    obj = kwargs.get("instance")

    if obj.is_removed is True:
        publisher.notify(
            event_type="DELETE_MEMBER",
            object_id=obj.id
        )
        return

    is_created = kwargs.get("created", False)

    if is_created:
        publisher.notify(
            event_type="CREATE_ORG_MEMBER",
            user_id=obj.user_id,
            organization_id=obj.organization_id
        )


# Custom signal for accepting invitation
if VERSION < (4, 0):
    accepting_invitation_client_signal = Signal(
        providing_args=["user_id", "client_id", "token"]
    )
else:
    accepting_invitation_client_signal = Signal()

if VERSION < (4, 0):
    accepting_invitation_organization_signal = Signal(
        providing_args=["user_id", "organization_id", "token"]
    )
else:
    accepting_invitation_organization_signal = Signal()


@receiver(accepting_invitation_client_signal)
def change_notification_client_status(sender, **kwargs):
    try:
        token = kwargs.get("token")
        user_id = kwargs.get("user_id")
        client_id = kwargs.get("client_id")
        meta = {
            "client_id": str(client_id),
            "type": "client",
            "invitation_token": token,
        }
        notification = Notification.objects.get(
            user_id=user_id, object_id=client_id, meta=meta
        )
        notification.status = NOTIFICATION_STATUS[1][0]
        notification.save()
    except Exception as err:
        logger.exception("change_notification_status SIGNAL:", err)


@receiver(accepting_invitation_organization_signal)
def change_notification_organization_status(sender, **kwargs):
    try:
        token = kwargs.get("token")
        user_id = kwargs.get("user_id")
        organization_id = kwargs.get("organization_id")
        meta = {
            "organization_id": str(organization_id),
            "type": "organization",
            "invitation_token": token,
        }
        notification = Notification.objects.get(
            user_id=user_id, object_id=organization_id, meta=meta
        )
        notification.status = NOTIFICATION_STATUS[1][0]
        notification.save()
    except Exception as err:
        logger.exception("change_notification_status SIGNAL:", err)
