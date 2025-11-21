from typing import Dict, List

from celery import current_app
from django.conf import settings
from django.db import transaction

from app.core.logger import logger
from app.tenancies.observer.crud_member.listener_create_org_member_effect import CreateOrgMemberEffectListener
from app.tenancies.observer.crud_member.listener_create_workspace_member_effect import (
    CreateWorkspaceMemberEffectListener)
from app.tenancies.observer.crud_member.listener_delete_member_effect import DeleteMemberEffectListener
from app.tenancies.observer.interface_listener import IListener
from app.tenancies.observer.org_member_role_changes.listener_org_member_clients_effect import (
    OrgMemberClientEffectListener)
from app.tenancies.observer.org_member_role_changes.listener_org_member_permissions_effect import (
    OrgMemberPermissionEffectListener)
from app.tenancies.observer.workspace.listener_create_app_profile import (
    CreateAppProfileListener,
)
from app.tenancies.observer.workspace.listener_create_client_module import (
    CreateClientModuleListener,
)
from app.tenancies.observer.workspace.listener_create_client_module_firebase import CreateClientModuleFirebaseListener
from app.tenancies.observer.workspace.listener_create_client_module_redis import CreateClientModuleRedisListener
from app.tenancies.observer.workspace.listener_grant_user_client_access import GrantUserClientAccessListener
from app.tenancies.observer.workspace.listener_send_approve_active_client import (
    SendEmailActiveClientListener,
)


@current_app.task(bind=True)
def observer_with_celery(self, event_type: str, *args, **kwargs):
    # ignore_result = False
    # name = "observer_with_celery"
    #
    # track_started = True

    logger.info(f"{self.__class__.__name__} with event {event_type}")
    for listener in publisher.event[event_type]:
        logger.info(f"{self.__class__.__name__} with event {event_type} - {listener.__class__.__name__}")
        listener.run(**kwargs)

    return {"observer_event_type": event_type, "parameters": kwargs}


class __Publisher:
    """
    Observer Pattern
    Manage typical actions on workspace, member
    """

    event: Dict[str, List[IListener]] = {
        "CREATE_WORKSPACE": [
            CreateAppProfileListener(),
            CreateClientModuleListener(),
            CreateClientModuleRedisListener(),
            CreateClientModuleFirebaseListener(),
            SendEmailActiveClientListener(),
            GrantUserClientAccessListener()
        ],
        "UPDATE_ORG_MEMBER_ROLE": [
            OrgMemberClientEffectListener(),
            OrgMemberPermissionEffectListener()
            # eg: push pub-sub notify permission
        ],
        "CREATE_ORG_MEMBER": [
            CreateOrgMemberEffectListener()
        ],
        "CREATE_WORKSPACE_MEMBER": [
            CreateWorkspaceMemberEffectListener()
        ],
        "UPDATE_WORKSPACE_MODULE": [
            CreateClientModuleRedisListener(),
            CreateClientModuleFirebaseListener()
        ],
        "DELETE_MEMBER": [
            DeleteMemberEffectListener()
        ]
    }

    event_countdown: Dict[str, int] = {
        "UPDATE_WORKSPACE_MODULE": 5
    }

    def subscribe(self, event_type: str, listener):
        # TODO: dynamically subscribe
        pass

    def unsubscribe(self, even_type: str):
        # TODO: dynamically unsubscribe
        pass

    def notify(self, event_type: str, **kwargs):
        if event_type not in self.event:
            raise Exception("key event error.")

        if settings.IS_CELERY_ENABLED:
            # commit db session is required in case of using celery
            # chain of actions in event are affected by state with the order
            countdown_secs = self.event_countdown.get(event_type, 0)
            transaction.on_commit(lambda: observer_with_celery.apply_async(
                (event_type,),
                kwargs=kwargs,
                countdown=countdown_secs
            ))
            return

        for listener in self.event[event_type]:
            listener.run(**kwargs)


publisher = __Publisher()
