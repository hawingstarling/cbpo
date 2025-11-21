import logging
from django.core.management.base import BaseCommand
from ...models import Organization, User, Client, UserClient, OrganizationUser, Role
from ...config_static_variable import ORGANIZATION_DEFAULT
from ...services import RoleService, OrganizationService
from django.db import transaction
from bulk_update.helper import bulk_update

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'our help string comes here'

    def handle(self, *args, **options):
        """
        Create Organization for sync client with not organization:
            1. Create organization default and make user default role Owner
            2. Make client not organization to organization default (keep role and permission)
            3. Make client users to Organization User with Role Client (If not exists)
            4. Don't send Notification and Email
        :param args: 
        :param options: 
        :return: 
        """
        email = "datgs@hdwebsoft.com"
        try:
            print("Begin sync client to organization ............")
            with transaction.atomic():
                user = User.objects.get(email=email)
                # Init organization default
                org, _ = Organization.objects.get_or_create(name=ORGANIZATION_DEFAULT, owner=user)

                # Get all client with organization is None
                clients = Client.objects.filter(active=True, organization__isnull=True)
                if not clients.exists():
                    return None
                clients_update = []
                for client in clients.iterator():
                    print("Client update : {}".format(client.name))
                    client.organization = org
                    clients_update.append(client)
                bulk_update(clients_update)
                #
                self.grant_access_manage_user_organization(organization=org, user=user, role=RoleService.role_owner())
                # get all user exists in user clients
                list_users_client = UserClient.objects.filter(client__in=clients_update).distinct().values_list(
                    'user_id', flat=True)

                # get all user client exists in organization
                list_create_organization = []

                for user_id in list_users_client.iterator():
                    if not OrganizationService.query_set_member_organization(organization=org,
                                                                             user_id=user_id).exists():
                        list_create_organization.append(
                            OrganizationUser(organization=org, user_id=user_id, role=RoleService.role_client()))

                OrganizationUser.objects.bulk_create(list_create_organization)
            print("Sync client to organization done")
        except User.DoesNotExist:
            logger.error("User with email {} not exist in systems. Please create user!".format(email))
            print("User with email {} not exist in systems. Please create user!".format(email))
        except Exception as ex:
            logger.error("Sync client to organization error {}".format(ex))
            print("Sync client to organization error {}".format(ex))

    def grant_access_manage_user_organization(self, user: User = None, organization: Organization = None,
                                              role: Role = None):
        """
        Grant access user manage organization:
            1. make user organization role Owner
            2. make user client role Owner
            3. make permission module is enabled
        :param user:
        :param organization:
        :param role:
        :return:
        """
        OrganizationUser.objects.update_or_create(organization=organization, user=user,
                                                  defaults={'role': role})
        #
        clients = list(Client.objects.filter(organization=organization, active=True))
        OrganizationService.grant_access_all_client_organization(clients=clients, users=[user],
                                                                 role=RoleService.role_owner())
