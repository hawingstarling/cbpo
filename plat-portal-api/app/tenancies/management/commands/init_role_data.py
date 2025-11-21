from django.core.management.base import BaseCommand
from django.db import transaction

from app.tenancies.models import Role
from app.tenancies.config_static_variable import role_name


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    '''using command 'python manage.py <init_role_data>'''

    def _create_tags(self):
        with transaction.atomic():
            try:
                #
                role_keys = [item.upper() for item in role_name]
                if Role.objects.filter(key__in=role_keys).count() < len(role_name):
                    print('Init Role Data............')
                    for i in role_name:
                        if Role.objects.filter(key=i.upper()).exists():
                            continue
                        Role.objects.get_or_create(
                            name=i,
                            key=i.upper())
            except ImportError:
                return

    def handle(self, *args, **options):
        self._create_tags()
