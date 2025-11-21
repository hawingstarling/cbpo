from django.core.management.base import BaseCommand
from django.db import transaction
from django_bulk_update.helper import bulk_update

from app.tenancies.models import UserModulePermission, UserClient, Client
from app.tenancies.config_static_variable import TUPLE_PERMISSION, MODULE_PERMISSION_MAP, MODULE_PERMISSION_ROG


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """
    remove BLOMAN in MAP Watcher
    """

    def _create_tags(self):
        clients = Client.objects.all()
        for i in clients:
            client = i
            user = i.owner
            self.restore_permission_BLOMAN(client, user)

        return

    def handle(self, *args, **options):
        self._create_tags()

    def restore_permission_BLOMAN(self, client, user):
        print('restore permission BLOMAN for owner of client: ', client.name)
        user_module_permission = UserModulePermission.objects.get(user=user,
                                                                  client=client,
                                                                  module='ROG',
                                                                  permission='BLOMAN')
        user_module_permission.enabled = True
        user_module_permission.save()
        return user_module_permission
