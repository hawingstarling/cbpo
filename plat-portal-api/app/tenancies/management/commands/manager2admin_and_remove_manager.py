from django.core.management.base import BaseCommand

from app.tenancies.models import UserClient, Client, Role
from app.tenancies.services import RoleService


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    """
    update admin to owner in each client
    """

    def _create_tags(self):
        role_manager = Role.objects.get(key='MANAGER')
        user_clients = UserClient.objects.filter(role=role_manager).all()
        print('change role manager to admin:')
        for i in user_clients:
            self.change_role_manager2admin(i)

        print('remove role manager')
        role_manager.delete()

        return

    def handle(self, *args, **options):
        self._create_tags()

    def change_role_manager2admin(self, user_client):
        role_admin = RoleService.role_admin()
        user_client.role = role_admin
        user_client.save()
        print(user_client, 'changed role manager to role admin')
        return user_client
