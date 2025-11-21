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
        clients = Client.objects.all()
        for i in clients:
            client = i
            user = i.owner
            self.change_role_admin2owner(client, user)

        return

    def handle(self, *args, **options):
        self._create_tags()

    def change_role_admin2owner(self, client, user):
        user_client = UserClient.all_objects.filter(client=client, user=user).first()
        # role_owner = RoleService.role_owner
        role_owner = Role.objects.get(key='OWNER')
        if user_client.role == role_owner:
            return user_client
        user_client.role = role_owner
        user_client.save()
        print(user_client, ' changed to owner')
        return user_client
