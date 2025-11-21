from django.core.management.base import BaseCommand
from app.tenancies.models import UserModulePermission
from django.db import transaction


class Command(BaseCommand):
    help = "Migrate remove permission mat_na_edit of MAT to user client role owner, admin."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        Remove permission mat_na_edit of MAT to user client
        :param args:
        :param options:
        :return:
        """
        print("Begin remove permission of MAT module")
        try:
            #
            with transaction.atomic():
                permission_lists = UserModulePermission.objects.filter(module="MT", permission="mat_na_edit")
                for _item in permission_lists:
                    print('Remove permissions mat_na_edit client : {} - user : {}'.format(_item.client.id,
                                                                                          _item.user.user_id))
                    _item.delete()
        except Exception as ex:
            print("Sync with error : {}".format(ex))
        print("End remove permission of MAT module")
