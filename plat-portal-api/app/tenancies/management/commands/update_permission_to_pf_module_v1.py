from bulk_sync import bulk_sync
from django.core.management.base import BaseCommand
from django.db.models import Q

from app.core.services.app_confg import AppService
from app.tenancies.models import ClientModule, Client


class Command(BaseCommand):
    help = "Migrate grant access permission of PF to user client role owner, admin."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        1. Get all client with active = True
        2. Grant permission PF to user client has role ["OWNER", "ADMIN"]
        :param args:
        :param options:
        :return:
        """
        print("Begin enabled module v1 of PF")
        try:
            app_name = "precise_financial"
            module_app = AppService.get_modules_app(app_name=app_name)
            clients = Client.objects.filter(active=True)
            #
            objs = []
            objs_revert_soft_delete = []
            for client in clients.iterator():
                print("client id: {}".format(str(client.pk)))
                for module in module_app:
                    print('module: {}'.format(module))
                    find = ClientModule.all_objects.filter(client=client, module=module).first()
                    if find:
                        if find.is_removed:
                            find.is_removed = False
                            find.enabled = True
                            objs_revert_soft_delete.append(find)
                        continue
                    obj = ClientModule(client=client, module=module, enabled=True, is_removed=False)
                    objs.append(obj)
            stats = {'stats': {'created': 0, 'updated': 0, 'deleted': 0}}
            if len(objs) > 0:
                stats = bulk_sync(
                    new_models=objs,
                    filters=Q(client__in=clients, module__in=module_app),
                    fields=['client_id', 'module', 'enabled', 'is_removed'],
                    key_fields=['client_id', 'module']
                )

            if len(objs_revert_soft_delete) > 0:
                stats['stats']['created'] += len(objs_revert_soft_delete)
                ClientModule.all_objects.bulk_update(objs_revert_soft_delete, ['enabled', 'is_removed'])
            print(stats)

        except Exception as ex:
            print("Sync with error : {}".format(ex))
        print("End enabled module v1 of PF")
