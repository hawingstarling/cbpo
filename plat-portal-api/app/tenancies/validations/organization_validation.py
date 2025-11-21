from app.tenancies.models import User, OrganizationUser, Organization
from app.core.exceptions import ObjectNotFoundException, MemberExistsException, UserInvitationException
from ..config_static_variable import MEMBER_STATUS


def validate_send_invitation(organization: Organization, user_invitee: User):
    try:
        invite = OrganizationUser.objects.get(organization=organization, user=user_invitee)
        if invite.status == MEMBER_STATUS[1][0]:
            raise UserInvitationException()
    except OrganizationUser.DoesNotExist:
        pass
    return True


def validate_resend_invitation(organization: Organization, user_invitee: User):
    try:
        invite = OrganizationUser.objects.get(organization=organization, user=user_invitee)
        if invite.status != MEMBER_STATUS[1][0]:
            raise MemberExistsException()
    except OrganizationUser.DoesNotExist:
        raise ObjectNotFoundException(message="User not found in Organization")
    return True
