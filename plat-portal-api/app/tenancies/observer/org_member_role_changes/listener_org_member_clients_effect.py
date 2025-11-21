from app.tenancies.config_static_variable import IS_MEMBER
from app.tenancies.models import Client, UserClient
from app.tenancies.observer.interface_listener import IListener
from app.tenancies.services import RoleService


class OrgMemberClientEffectListener(IListener):
    def run(self, **kwargs):
        """
        update [UserClient] status and role in all clients
        create new [UserClient] with clients unless it exist
        """
        user_id, organization_id = kwargs.get("user_id"), kwargs.get("organization_id")
        client_ids = Client.objects.filter(organization_id=organization_id).values_list(
            "id", flat=True)

        data = {
            "status": IS_MEMBER,
            "role": RoleService.role_owner()
        }

        # update
        user_clients_exist = UserClient.all_objects.filter(
            client__id__in=client_ids, user_id=user_id)
        if len(user_clients_exist):
            user_clients_exist.update(
                is_removed=False, **data
            )
        update_obj_id_res = [ele.client_id for ele in user_clients_exist]

        # create
        clients_user_does_not_exist = [ele for ele in client_ids if ele not in update_obj_id_res]

        new_bulk_create_objs = [UserClient(user_id=user_id, client_id=ele, **data)
                                for ele in clients_user_does_not_exist]

        if len(new_bulk_create_objs):
            UserClient.objects.bulk_create(new_bulk_create_objs)
        return
