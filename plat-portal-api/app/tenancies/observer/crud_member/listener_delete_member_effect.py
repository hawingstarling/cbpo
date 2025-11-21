from app.permission.models import OrgClientCustomRoleUser, OverridingOrgClientUserPermission, OrgClientUserPermission
from app.tenancies.observer.interface_listener import IListener


class DeleteMemberEffectListener(IListener):
    def run(self, **kwargs):
        """
        delete custom roles created by the user
        delete override permission
        delete permission
        """
        object_id = kwargs.get("object_id")
        # object_id is user_client_id or organization_member_id

        OrgClientCustomRoleUser.objects.filter(object_id=object_id).delete()
        OverridingOrgClientUserPermission.objects.filter(object_id=object_id).delete()
        OrgClientUserPermission.objects.filter(object_id=object_id).delete()
