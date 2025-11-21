from django.contrib.auth.models import AnonymousUser

from app.core.exceptions import InvalidParameterException
from app.permission.config_static_varible.common import CLIENT_LEVEL_KEY, ORG_LEVEL_KEY
from app.permission.exceptions import UserClientMemberException
from app.permission.models import AccessRule, CustomRole, ClientUserProxy, OrganizationUserProxy
from app.tenancies.models import Client, Organization


class OrgClientBaseView(object):
    def get_client(self):
        client_id = self.kwargs.get('client_id', None)
        if not client_id:
            return None
        try:
            client = Client.objects.get(pk=client_id)
        except Exception:
            raise InvalidParameterException(message="parameter 'client_id' is invalid.")

        return client

    def get_user_client(self, user, client):
        try:
            return ClientUserProxy.objects.get(user=user, client=client)
        except ClientUserProxy.DoesNotExist:
            raise UserClientMemberException()

    def get_generic_obj_user_current(self):
        level = self.get_level_view()
        content_obj = self.get_content_obj()
        #
        generic_obj_user = None
        if level == ORG_LEVEL_KEY:
            generic_obj_user = OrganizationUserProxy.objects.get(user=self.request.user, organization=content_obj)
        if level == CLIENT_LEVEL_KEY:
            generic_obj_user = ClientUserProxy.objects.get(user_id=self.request.user.pk, client=content_obj)
        if not generic_obj_user and not isinstance(self.request.user, AnonymousUser):
            raise InvalidParameterException(message="generic user current level must in [OrgUser, ClientUser]")
        return generic_obj_user

    def get_org(self):
        org_id = self.kwargs.get('organization_id', None)
        if not org_id:
            return None
        try:
            org = Organization.objects.get(pk=org_id)
        except Exception:
            raise InvalidParameterException(message="parameter 'organization_id' is invalid.")

        return org

    def get_user_org(self, user, org):
        try:
            return OrganizationUserProxy.objects.get(user=user, organization=org)
        except OrganizationUserProxy.DoesNotExist:
            raise UserClientMemberException('User does not belong to the Organization')

    def get_client_ids(self):
        level = self.get_level_view()
        if level not in [ORG_LEVEL_KEY]:
            return []
        return list(self.get_content_obj().client_set.values_list('id', flat=True))

    def get_level_view(self):
        level = None
        if 'organization_id' in self.kwargs:
            level = ORG_LEVEL_KEY
        if 'client_id' in self.kwargs:
            level = CLIENT_LEVEL_KEY
        if not level and not isinstance(self.request.user, AnonymousUser):
            raise InvalidParameterException(message="level must in [Org, Client]")
        return level

    def get_content_obj(self):
        level = self.get_level_view()
        args = {
            ORG_LEVEL_KEY: self.get_org(),
            CLIENT_LEVEL_KEY: self.get_client()
        }
        content_obj = args.get(level)
        if not content_obj and not isinstance(self.request.user, AnonymousUser):
            raise InvalidParameterException(message="level must in [Org, Client]")
        return content_obj

    def get_content_object_user(self, user):
        level = self.get_level_view()
        args = {
            ORG_LEVEL_KEY: self.get_org(),
            CLIENT_LEVEL_KEY: self.get_client()
        }
        content_obj = args.get(level)
        return self.get_user_org(user, content_obj) if level == ORG_LEVEL_KEY else self.get_user_client(user,
                                                                                                        content_obj)

    def get_object_ids(self):
        if isinstance(self.request.user, AnonymousUser):
            return []
        content_object = self.get_content_obj()
        # filter by client_id, organization_id
        list_object_ids = [content_object.id]

        level = self.get_level_view()

        if level == ORG_LEVEL_KEY:
            #  get org id and all child client ids
            client_ids = Client.objects.filter(organization_id=content_object.id) \
                .distinct('id').values_list('id', flat=True)
            list_object_ids.extend(client_ids)
        else:
            #  get client id and parent org id
            list_object_ids.append(content_object.organization_id)
        return list_object_ids

    def get_object_id(self):
        if isinstance(self.request.user, AnonymousUser):
            return []
        content_object = self.get_content_obj()
        return [content_object.id]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['object_ids'] = self.get_object_ids()
        context['object_id'] = self.get_object_id()
        context['level'] = self.get_level_view()
        return context


class ClientAccessRuleBaseView(OrgClientBaseView):
    def get_access_rule(self):
        access_rule_id = self.kwargs.get('pk', None)
        if not access_rule_id:
            return None
        try:
            access_rule = AccessRule.objects.get(pk=access_rule_id)
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")
        return access_rule


class ClientCustomRoleBaseView(OrgClientBaseView):
    def get_custom_role(self):
        custom_role_id = self.kwargs.get('pk', None)
        if not custom_role_id:
            return None
        try:
            custom_role = CustomRole.objects.get(pk=custom_role_id)
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")
        return custom_role
