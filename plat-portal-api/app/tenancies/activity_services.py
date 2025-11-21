import re
from app.tenancies.config_static_variable import ACTION_ACTIVITY_OBJ
from .config_static_variable import (
    ACTION_ACTIVITY,
    MEMBER_STATUS,
    MODULE_ENUM,
)
from .config_app_and_module import LIST_APP_CONFIG
from app.tenancies.config_static_variable import ACTION_ACTIVITY_OBJ
from django.db.models import Q
from .models import (
    Activity,
    User,
    Client,
    OrganizationUser,
    UserClient
)
from app.core.logger import logger

class ActivityService:
    @staticmethod
    def action_sign_in():
        return "SIGN_IN"
    
    @staticmethod
    def action_add_member():
        return "ADD_MEMBER"

    @staticmethod
    def action_update_member():
        return "UPDATE_MEMBER"
        
    @staticmethod
    def action_delete_member():
        return "DELETE_MEMBER"

    @staticmethod
    def action_download_map_report():
        return "DOWNLOAD_MAP_REPORT"

    @staticmethod
    def action_download_rog_report():
        return "DOWNLOAD_ROG_REPORT"

    @staticmethod
    def action_access_workspace():
        return "ACCESS_WORKSPACE"

    @staticmethod
    def get_list_action():
        return dict(ACTION_ACTIVITY).keys()

    @staticmethod
    def get_key_search_field_data():
        return ["client_name", "report_name", "app_profile", "module"]

    @staticmethod
    def get_query_set_activity(user: User = None, **kwargs):
        queryset = Activity.objects.all()
        if user:
            queryset = queryset.filter(user=user)
        if kwargs:
            queryset = queryset.filter(**kwargs)
        return queryset

    @staticmethod
    def find_action_from_key(data: str):

        result = None

        try:
            data = data.strip()  # clean space white begin, end of key input

            action_keys = [
                f"{key}-{value}" for key, value in ACTION_ACTIVITY_OBJ.items()
            ]

            for action in action_keys:

                val = action.split("-")

                find = (
                        re.search(val[0], data, re.IGNORECASE)
                        or re.search(val[1], data, re.IGNORECASE)
                        or re.search(val[0].replace("_", " "), data, re.IGNORECASE)
                        or re.search(val[1].replace("_", " "), data, re.IGNORECASE)
                )
                if find:
                    return val[0]
        except Exception as ex:
            logger.error(f"[find_action_from_key] : {ex}")

        return result

    @staticmethod
    def get_queryset_filter_action_by_client_id(client_id: str, action: str):
        condition = Q(object_id=client_id)
        if action:
            condition = Q(object_id=client_id, action=action)

        return condition

    @staticmethod
    def get_queryset_filter_action_object(
            action: str = None, key: str = None, object: any = None, object_ids: list = [], **kwargs
    ):
        """
        Filter queryset by request
            1. Action
            2. key word for search in username, email, and field data json contain key and value
            3. Special case action SPECIAL_ACTION = SIGN_IN, ADD_MEMBER, UPDATE_MEMBER, DELETE_MEMBER:
                a. User login not determine object (Client, Organization) object = None
                b. if filter activity have Object (Client, Organization)
                    filter = (activity of Object - SPECIAL_ACTION) + SPECIAL_ACTION user exist in Object(Client , Organization)
                c. if filter activity not Object
                    filter = action of activity
        :param action:
        :param key:
        :param object:
        :param object_ids:
        :return:
        """
        organization = kwargs.get("organization", None)
        condition_object = None
        actions_cond = None
        condition_action = None
        condition_key = None
        user_ids = set()  # Initialize as a set to ensure uniqueness
        actions = [
            ActivityService.action_sign_in(),
            ActivityService.action_add_member(),
            ActivityService.action_update_member(),
            ActivityService.action_delete_member()
        ]
        if(organization):
            # get all member users in organization user table
            user_ids.update(OrganizationUser.objects.filter(
                organization=organization, status=MEMBER_STATUS[0][0]
            ).values_list("user_id", flat=True))

        # check object is Client
        if object is Client:
            condition_object = Q(object_id__in=object_ids)
            # find all member users in user client table
            user_ids.update(UserClient.objects.filter(
                client_id__in=object_ids, status=MEMBER_STATUS[0][0]
            ).values_list("user_id", flat=True))
            
            actions_cond = Q(action__in=actions, user_id__in=user_ids)
        # filter action
        if action:
            if (action in actions) and condition_object:
                # if action in one of these (SIGN_IN, ADD_MEMBER, UPDATE_MEMBER, DELETE_MEMBER)
                condition_action = Q(action=action, user_id__in=user_ids)
            else:
                condition_action = (
                    condition_object & Q(action=action)
                    if condition_object
                    else Q(action=action)
                )
        # filter key
        if key:
            #
            condition_key = (
                    Q(user__username__icontains=key)
                    | Q(user__email__icontains=key)
                    | Q(user__first_name__icontains=key)
                    | Q(user__last_name__icontains=key)
            )
            for item in ActivityService.get_key_search_field_data():
                condition_key |= Q(data__contains={item: key})
            # Search key in list project name config and list module name config
            list_app_config = dict(LIST_APP_CONFIG)
            apps_config = [
                k.lower()
                for k in list_app_config.keys()
                if key.lower() in list_app_config[k].lower()
            ]
            for item in apps_config:
                condition_key |= Q(data__contains={"app_profile": item})
            list_module_config = dict(MODULE_ENUM)
            modules = [
                k.upper()
                for k in list_module_config.keys()
                if key.lower() in list_module_config[k].lower()
            ]
            for item in modules:
                condition_key |= Q(data__contains={"module": item})
            #
            condition_key = (
                (condition_object & condition_key) | (actions_cond & condition_key)
                if condition_object
                else condition_key
            )
        #
        if not condition_action and not condition_key:
            conditions = condition_object | actions_cond if condition_object else None
        elif not condition_action and condition_key:
            conditions = condition_key
        elif action and not condition_key:
            conditions = condition_action
        else:
            conditions = condition_action & condition_key

        # find action by key input
        if not action and key:
            action_by_key = ActivityService.find_action_from_key(data=key)

            if action_by_key:
                if action_by_key == "SIGN_IN":
                    # because login not detect ws object
                    condition_action_by_key = (
                        Q(action="SIGN_IN", user_id__in=user_ids)
                        if condition_object
                        else Q(action="SIGN_IN")
                    )
                else:
                    condition_action_by_key = (
                        condition_object & Q(action=action_by_key)
                        if condition_object
                        else Q(action=action_by_key)
                    )

                conditions = conditions | condition_action_by_key

        return conditions

    @staticmethod
    def create_activity(user: User = None, action: str = None, data: dict = {}, **kwargs):
        Activity.objects.create(user=user, action=action, data=data, **kwargs)