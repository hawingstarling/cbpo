from django.core.management.base import BaseCommand
from django.db import transaction
from django_bulk_update.helper import bulk_update

from app.tenancies.models import UserModulePermission, UserClient
from app.tenancies.config_static_variable import TUPLE_PERMISSION, MODULE_PERMISSION_MAP, MODULE_PERMISSION_ROG


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """
    script command to fulfill exactly 8 permissions.
    Each member in client who already exists just has 6 permissions
    make them uniquely in Model UserModulePermission
    """

    def _create_tags(self):
        all_members = UserClient.all_objects.all()
        chosen_members = [item for item in all_members if self.choose_member(item)]

        print('list member are going to be expanded permissions:')
        for k, i in enumerate(chosen_members):
            print(k, ': ', i)

        list_user_client_permissison_for_bulk_create = []

        for item in chosen_members:
            list_user_client_permissison_for_bulk_create.extend(self.expanding_permissions(item))

        print('list permissions are going to be bulk create:')
        for k, i in enumerate(list_user_client_permissison_for_bulk_create):
            print(k, ': ', i)

        UserModulePermission.objects.bulk_create(list_user_client_permissison_for_bulk_create)

        return

    def handle(self, *args, **options):
        self._create_tags()

    def choose_member(self, user_client):
        """
        check object member in client need to be fulfill permissions
        :return: object
        """
        current_number_of_permission = len(TUPLE_PERMISSION)

        if UserModulePermission.all_objects.filter(user_client=user_client)\
                .all().count() < current_number_of_permission:
            return True
        return False

    def expanding_permissions(self, user_client):
        """
        adding new permission for a specific member
        :param user_client:
        :return: list user_client_permission
        """
        enabled = True if user_client.is_admin_or_manager() else False
        result = []
        permission_list = list(MODULE_PERMISSION_MAP + MODULE_PERMISSION_ROG)
        for module, permission in permission_list:
            # this permission already exists -> ignore
            if UserModulePermission.all_objects.filter(module=module,
                                                       permission=permission[0],
                                                       client=user_client.client,
                                                       user=user_client.user,
                                                       user_client=user_client)\
                    .exists():

                continue

            # new permission
            user_module_permission = UserModulePermission(
                module=module,
                permission=permission[0],
                client=user_client.client,
                user=user_client.user,
                user_client=user_client,
                enabled=enabled)

            result.append(user_module_permission)

        return result
