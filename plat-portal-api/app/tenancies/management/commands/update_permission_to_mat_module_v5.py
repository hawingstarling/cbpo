from django.core.management.base import BaseCommand
from app.tenancies.models import ClientModule, UserModulePermission, UserClient, Client
from django.db import transaction
from app.tenancies.config_static_variable import MEMBER_STATUS, MODULE_PERMISSION_MAP, MODULE_PERMISSION_MT, \
    MODULE_PERMISSION_DS, MODULE_PERMISSION_RA


class Command(BaseCommand):
    help = "Migrate grant access permission of MAT to user client role owner, admin."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        1. Get all client with active = True
        2. Grant permission MAT to user client has role ["OWNER", "ADMIN"]
        :param args:
        :param options:
        :return:
        """
        print("Begin update permission of MAT module")
        try:
            # 1
            client_ids = Client.objects.filter(active=True).values_list('pk', flat=True)
            #
            objs = []
            permission_update = MODULE_PERMISSION_MAP + MODULE_PERMISSION_MT + MODULE_PERMISSION_DS + MODULE_PERMISSION_RA
            for client_id in client_ids:
                print("Grant access permission for client : {}".format(client_id))
                # 2
                user_ids = UserClient.objects.filter(client_id=client_id,
                                                     role__key__in=['OWNER', 'ADMIN'],
                                                     status=MEMBER_STATUS[0][0]).values_list('user_id', flat=True)
                for user_id in user_ids:
                    user_client = UserClient.objects.get(user_id=str(user_id), client_id=str(client_id))
                    for module, _permissions in permission_update:
                        find = UserModulePermission.objects.filter(
                            user_id=user_id, client_id=client_id,
                            module=module,
                            permission=_permissions[0],
                            user_client=user_client)
                        if not find.exists():
                            print("Grant module {} with permission {}".format(module, _permissions[0]))
                            obj = UserModulePermission(user_id=user_id, client_id=client_id, module=module,
                                                       permission=_permissions[0],
                                                       user_client=user_client, enabled=True)
                            objs.append(obj)
            with transaction.atomic():
                UserModulePermission.objects.bulk_create(objs, ignore_conflicts=True)
        except Exception as ex:
            print("Sync with error : {}".format(ex))
        print("End update permission of MAT module")
