import ast

from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.db.models import CharField
from django.db.models.functions import Cast
from app.financial.models import ClientPortal
from app.job.utils.helper import register_list
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY


class Command(BaseCommand):
    help = "Create command run on celery."

    def add_arguments(self, parser):
        parser.add_argument('-m', '--module', type=str, help='Provide module name')
        parser.add_argument('-c', '--client_id', type=str, help='Provide client id')
        parser.add_argument('-k', '--kwargs', type=str, help='Provide kwarg')

    def handle(self, *args, **options):
        print('----------Begin create command run in celery-------------')
        module = options['module']
        if not module:
            print('Please input module position')
            return
        client_id = options['client_id']
        kwargs = options['kwargs']
        if not kwargs:
            kwargs = "{}"
        kwargs = ast.literal_eval(kwargs)
        if not client_id:
            client_ids = list(ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True) \
                              .annotate(client_id=Cast('pk', CharField())).values_list('client_id', flat=True))
        else:
            client_ids = [str(client_id)]
        print(f'----------Register for client ids = {client_ids}')
        data = []
        for client_id in client_ids:
            kwargs.update(client_id=client_id)
            data.append(dict(
                client_id=client_id,
                name=f"run_command_for_{module.split('.')[-1]}",
                job_name="app.core.jobs.command.run_command_by_celery",
                module="app.core.jobs.command",
                method="run_command_by_celery",
                meta=dict(module=module, kwargs=kwargs),
                time_limit=None
            ))
        register_list(category=SYNC_DATA_SOURCE_CATEGORY, data=data)
