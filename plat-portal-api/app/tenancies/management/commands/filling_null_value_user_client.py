from django.core.management.base import BaseCommand
from django.db import transaction
from django_bulk_update.helper import bulk_update

from app.tenancies.models import UserModulePermission, UserClient


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """filling null value for column user_client in Model UserModulePermission"""

    def _create_tags(self):
        with transaction.atomic():
            try:
                user_module_permission = UserModulePermission.objects.filter(user_client=None).all()
                if user_module_permission.count() == UserModulePermission.objects.all().count():
                    def change_null(x): return UserClient.objects.filter(user=x.user, client=x.client).first()
                    for k, v in enumerate(user_module_permission):
                        v.user_client = change_null(v)
                        print(k)

                    bulk_update(user_module_permission, update_fields=['user_client_id'])

            except Exception as ex:
                raise ex

    def handle(self, *args, **options):
        self._create_tags()
