from django.core.management.base import BaseCommand
from app.tenancies.models import Client, ClientModule, UserModulePermission, UserClient
from django.db.models import Q, Count
from app.core.services.app_confg import AppService
from app.tenancies.config_static_variable import MEMBER_STATUS
from django.db import transaction


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        1. Get all client module missing new configuration
        2. Update module missing for client module
        3. Update permission with all user permission module role ['OWNER', ADMIN] in client user
        :param args:
        :param options:
        :return:
        """
        print("Begin sync module to client of app")
        try:
            # 1
            client_ids = Client.objects.all().values_list('pk')
            clients_ids_module = ClientModule.objects.filter(client_id__in=client_ids).values('client_id').annotate(
                dcount=Count('client_id'))
            # 2
            number_module = len(AppService.get_all_modules_app())
            client_ids_module_update = []
            for item in clients_ids_module:
                if item['dcount'] != number_module:
                    client_ids_module_update.append(item['client_id'])

            with transaction.atomic():
                # 3
                permission_dc = AppService.get_permissions_app(app_name="data_central", module_name="DC")
                print("Permission module DC Update : {}".format(permission_dc))
                for client_id in client_ids_module_update:
                    print("Update module DC for client id : {}".format(client_id))
                    find_obj = ClientModule.objects.filter(client_id=client_id, module="DC")
                    if find_obj.exists():
                        continue
                    ClientModule.objects.get_or_create(client_id=client_id, module="DC", enabled=True)
                # 4
                client_ids_module_dc = ClientModule.objects.filter(module="DC", enabled=True).values_list('client_id',
                                                                                                          flat=True)
                for client_id in client_ids_module_dc:
                    grant_client_user_ids = UserClient.objects.filter(client_id=client_id,
                                                                      role__key__in=["OWNER", "ADMIN"],
                                                                      status=MEMBER_STATUS[0][0]).values_list('user_id',
                                                                                                              flat=True)
                    print("Grant permission for list users : {}".format(grant_client_user_ids))
                    self.grant_permission_for_module_of_client(client_id=client_id,
                                                               client_user_ids=grant_client_user_ids,
                                                               permission_list=permission_dc)
        except Exception as ex:
            print("Sync with error : {}".format(ex))
        print("End sync module to client of app")

    def grant_permission_for_module_of_client(self, client_id: str = None, client_user_ids: list = [], module="DC",
                                              permission_list: list = []):
        """
        :param client:
        :param client_users:
        :param module:
        :param permission_dc:
        :return:
        """
        for user_id in client_user_ids:
            user_client = UserClient.objects.get(user_id=user_id, client_id=client_id)
            #
            permissions_user_import = []
            for permission in permission_list:
                print("permission : {}".format(permission))
                find = UserModulePermission.objects.filter(
                    client_id=client_id,
                    user_id=user_id,
                    module=module,
                    permission=permission[0],
                    user_client=user_client)
                if find.exists():
                    continue
                user_module_permission = UserModulePermission(
                    client_id=client_id,
                    user_id=user_id,
                    module=module,
                    permission=permission[0],
                    user_client=user_client,
                    enabled=True
                )
                permissions_user_import.append(user_module_permission)
            UserModulePermission.objects.bulk_create(permissions_user_import)
