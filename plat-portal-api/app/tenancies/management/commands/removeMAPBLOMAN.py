from django.core.management.base import BaseCommand
from django.db import transaction
from django_bulk_update.helper import bulk_update

from app.tenancies.models import UserModulePermission, UserClient
from app.tenancies.config_static_variable import TUPLE_PERMISSION, MODULE_PERMISSION_MAP, MODULE_PERMISSION_ROG


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """
    remove BLOMAN in MAP Watcher
    """

    def _create_tags(self):
        print('Delete all BLOMAN permission in MAP watcher:')
        list_bloman_permission = UserModulePermission.all_objects.filter(module='MAP', permission='BLOMAN').all()
        for i in list_bloman_permission:
            print(i)
            i.delete()

    def handle(self, *args, **options):
        self._create_tags()
