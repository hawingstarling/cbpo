import abc
import re

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.db.models import QuerySet
from rest_framework import generics, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.views import APIView

from app.core.logger import logger
from app.core.pagination import OrganizationClientResultsSetPagination
from app.core.utils import *
from app.tenancies.validations.organization_validation import validate_send_invitation, validate_resend_invitation
from .common import AppBaseView
from .common import RequestLogMiddleware
from ..config_app_and_module import LIST_APP_CONFIG, APP_NAME_BUILD_PROFILE, APP_BUILD_TRANSIT
from ..models import User, Client, Organization
from ..permissions import (
    UserCanCreateClient, IsOrganizationAction, IsOrganizationUserAction, IsOrganizationUserCreateClient,
    IsOrganizationUserActionUpdateRole, LimitNewClientFromPermission, LimitInternalUserPermission,
    LimitNewOrgDefaultPermission, LimitNewClientDefaultPermission)
from ..serializers import (
    ClientSerializer, OrganizationSerializer, OrganizationUserSerializer, UpdateRoleUserOrganizationSerializer,
    OrganizationInvitationSerializer, OrganizationValidateTokenSerializer, OrganizationResendInvitationSerializer,
    OrganizationClientSerializer, OrganizationAccessClientSerializer, UserInfoOrganizationClientSerializer,
    RoleSerializer, OrganizationClientsModulesSerializer, AppClientConfigSerializer, AppClientConfigSwitcherSerializer,
    ForceOrganizationInvitationSerializer)
from ..services import OrganizationService, EmailService, OrganizationRoleService, \
    UserClientService, ClientService, AppClientConfigService
from ..activity_services import ActivityService
from app.core.simple_authentication import get_app_name_from_request
from ...permission.services.compose_permission_service import ComposePermissionService
from app.tenancies.tasks import log_activity_task


class OrganizationRegisterView(RequestLogMiddleware, generics.ListCreateAPIView):
    """
    Create register organization
    """
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if hasattr(self.request, 'method') and self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated]
        else:
            app_name = get_app_name_from_request(self.request)
            permissions_list = [IsAuthenticated, UserCanCreateClient]
            if app_name != APP_BUILD_TRANSIT:
                permissions_list = [IsAuthenticated, UserCanCreateClient, LimitNewOrgDefaultPermission]
            self.permission_classes = permissions_list
        return super(OrganizationRegisterView, self).get_permissions()

    def get_queryset(self):
        return OrganizationService.get_organizations(user=self.request.user)


class OrganizationBaseView(AppBaseView):
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthenticated, IsOrganizationAction)

    def get_queryset(self):
        return None

    def get_object(self):
        query_set = self.get_queryset()
        if not query_set or not query_set.exists():
            raise ObjectNotFoundException('Object not found in Organization')
        return query_set.first()

    @property
    def get_user_current(self):
        return self.request.user

    @property
    def get_user_request(self):
        user_id = self.kwargs.get('user_id', None)
        if not user_id:
            return None
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise InvalidParameterException("parameter 'user_id' is invalid.")

    @property
    def get_organization(self):
        pk = self.kwargs.get('pk', None)
        if not pk:
            return None
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise InvalidParameterException("parameter 'pk' is invalid.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "organization": self.get_organization
        })
        return context

    def get_client(self):
        try:
            client = Client.objects.get(pk=self.kwargs.get('client_id'))
        except Exception:
            raise InvalidParameterException(message="parameter 'client_id' is invalid.")
        return client

    def get_organization_user_role_current(self):
        if not self.request.user.pk and not self.kwargs.get('pk', None):
            return None
        try:
            user_role = OrganizationRoleService.get_query_set_role_user(organization=self.get_organization,
                                                                        user=self.get_user_current).first()
            if user_role:
                return user_role.role
            return None
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")

    def get_organization_user_role_request(self):
        if not self.kwargs.get('user_id', None) and not self.kwargs.get('pk', None):
            return None
        try:
            user_request = self.get_user_request
            user_role = OrganizationRoleService.get_query_set_role_user(organization=self.get_organization,
                                                                        user=user_request).first()
            if user_role:
                return user_role.role
            return None
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")


class OrganizationActionView(RequestLogMiddleware, OrganizationBaseView, generics.RetrieveUpdateDestroyAPIView):
    """
    Update organization
    """

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return OrganizationService.get_organizations(pk=pk, user=self.request.user)


class OrganizationClientView(RequestLogMiddleware, OrganizationBaseView, generics.ListAPIView, generics.GenericAPIView):
    """
    List , Create client to Organization
    """
    serializer_class = OrganizationClientSerializer
    permission_classes = (IsAuthenticated, IsOrganizationUserCreateClient)

    def get_permissions(self):
        self.permission_classes = (IsOrganizationUserCreateClient,)
        if self.request.method == 'GET':
            return super().get_permissions()
        else:
            app_name = get_app_name_from_request(self.request)
            if app_name == APP_BUILD_TRANSIT:
                self.permission_classes = (IsOrganizationUserCreateClient, LimitNewClientFromPermission)
            else:
                self.permission_classes = (IsOrganizationUserCreateClient, LimitNewClientDefaultPermission)
        return super().get_permissions()

    def filter_by_module(self, queryset: QuerySet = None):
        if not queryset:
            return queryset
        module = self.request.query_params.get('module', None)
        if module and module in list(get_all_module_enum_profile().keys()):
            module = re.sub(r'[^\w]', '', module)
            queryset = queryset.filter(clientmodule__module=module, clientmodule__enabled=True)
        return queryset

    def filter_app_profile(self, queryset: QuerySet = None):
        if not queryset:
            return queryset
        app_profile = self.request.query_params.get('app_profile', None)
        # Join check config app client
        if app_profile:
            app_profile = re.sub(r'[^\w]', '', app_profile)
            queryset = AppClientConfigService.get_client_query_set_join_client_app_profile(queryset=queryset,
                                                                                           app_profile=app_profile)
        return queryset

    def get_queryset(self):
        """
        QuerySet filter client
            1. status client
            2. app profile client have enabled in model AppClientConfig
            3. filter by module of client have enabled
        :return:
        """
        # get status query set
        status = self.request.query_params.get('status', None)
        key = self.request.query_params.get('key', None)
        if not status and status not in ['all', 'enabled', 'pending']:
            status = "all"
        status = status.lower()
        # build query set
        queryset = OrganizationService.query_set_client_organization(organization=self.get_organization,
                                                                     role=self.get_organization_user_role_current(),
                                                                     user=self.get_user_current,
                                                                     status=status).order_by('name')
        if key:
            search_key = Q(name__icontains=key)
            queryset = queryset.filter(search_key)
        # filter by app client profile
        queryset = self.filter_app_profile(queryset=queryset)
        # filter by module
        queryset = self.filter_by_module(queryset=queryset)
        return queryset

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            #
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        except Exception as ex:
            raise ex


class OrganizationClientUpdateDeleteView(RequestLogMiddleware, OrganizationBaseView,
                                         generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update , Delete client to Organization
    """
    serializer_class = ClientSerializer

    def get_queryset(self):
        return Client.objects.filter(pk=self.kwargs.get('client_id', None))

    def unique_name_client(self, request):
        data = request.data
        organization = self.get_organization
        client = self.get_client()
        if 'name' in data and data['name']:
            ClientService.unique_name_client(name=data['name'], organization=organization, client=client)

    def put(self, request, *args, **kwargs):
        self.unique_name_client(request=request)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.unique_name_client(request=request)
        return super().patch(request, *args, **kwargs)


class OrganizationUserListView(RequestLogMiddleware, OrganizationBaseView,
                               generics.ListAPIView):
    """
    List user of Organization
    """
    serializer_class = OrganizationUserSerializer

    def get_queryset(self):
        roles = self.request.GET.getlist('roles[]', [])
        key = self.request.query_params.get('key', None)
        queryset = OrganizationService.query_set_member_organization(organization=self.get_organization)
        if roles:
            roles = [re.sub(r'[^\w]', '', item).upper() for item in roles]
            queryset = queryset.filter(role__key__in=roles)
        if key:
            conditions = Q(user__username__icontains=key) | Q(user__email__contains=key) | Q(
                user__first_name__icontains=key) | Q(user__last_name__icontains=key)
            queryset = queryset.filter(conditions)
        return queryset.order_by('created')


class OrganizationUserView(RequestLogMiddleware, OrganizationBaseView,
                           generics.RetrieveDestroyAPIView):
    """
    Update , Delete client to Organization
    """
    serializer_class = OrganizationUserSerializer
    permission_classes = (IsAuthenticated, IsOrganizationUserAction,)

    def get_queryset(self):
        return OrganizationService.query_set_member_organization(organization=self.get_organization,
                                                                 user=self.get_user_request)

    def destroy(self, request, *args, **kwargs):
        try:
            if self.request.user == self.get_user_request:
                raise InvalidParameterException(message="You can't delete yourself")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            delete_option = serializer.validated_data.get("delete_option", None)

            # checking whether user exists in Workspaces
            if not delete_option and OrganizationService.check_user_in_WS(self.get_organization, self.get_user_request):
                return Response(data={"message": "User exists in workpaces"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            if delete_option == "DELETE_ALL":
                OrganizationService.destroy_access_user_organization(
                    organization=self.get_organization,
                    user=self.get_user_request)
            elif delete_option == "DELETE_AND_KEEP_IN_WS":  # delete user in org and change to external user
                OrganizationService.delete_org_user_only(self.get_organization, self.get_user_request)
            else:
                OrganizationService.query_set_member_organization(
                    organization=self.get_organization, user=self.get_user_request
                ).delete()

            # Log delete member activity
            data = {"Full name": f"{self.get_user_request.first_name} {self.get_user_request.last_name}",
                    "Email": self.get_user_request.email}
            log_activity_task.delay(user_id=request.user.pk, action=ActivityService.action_delete_member(), data=data)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            raise GenericException(message=ex)


class OrganizationRetrieveClientUserView(RequestLogMiddleware, OrganizationBaseView,
                                         generics.ListAPIView):
    """
    Organization retrieve client can grant to user
    """
    serializer_class = OrganizationClientSerializer
    pagination_class = OrganizationClientResultsSetPagination

    def get_serializer_context(self):
        context = super(OrganizationRetrieveClientUserView, self).get_serializer_context()
        context.update({
            "user_request": self.get_user_request
        })
        return context

    def get_queryset(self):
        role = self.get_organization_user_role_request()
        if not role and not isinstance(self.request.user, AnonymousUser):
            raise InvalidParameterException(message="User has not been invited to organization.")
        return OrganizationService.query_set_client_organization(organization=self.get_organization).order_by('name')


class OrganizationUserUpdateRoleView(RequestLogMiddleware, OrganizationBaseView,
                                     generics.UpdateAPIView):
    """
    Update user role organization
    """
    serializer_class = UpdateRoleUserOrganizationSerializer
    permission_classes = (IsAuthenticated, IsOrganizationUserActionUpdateRole)

    def get_queryset(self):
        return OrganizationService.query_set_member_organization(organization=self.get_organization,
                                                                 user=self.get_user_request)


class OrganizationUserInvitationView(RequestLogMiddleware, OrganizationBaseView, generics.GenericAPIView):
    serializer_class = OrganizationInvitationSerializer

    def get_user_invitee(self):
        email = self.request.data.get('email', None)
        try:
            return User.objects.filter(email=email.lower()).first()
        except User.DoesNotExist:
            logger.debug('Get USer Invitation Organization Error : {}'.format(email))
            raise ObjectNotFoundException('Email invitation not correct!')

    def post(self, request, *args, **kwargs):
        try:
            organization = self.get_organization
            serializer = self.serializer_class(data=request.data, context={'organization': organization,
                                                                           'request': request,
                                                                           'admin': request.user,
                                                                           'app_name': self.get_app_name_profile,
                                                                           })
            serializer.is_valid(raise_exception=True)
            # create new user without exist
            if serializer.advanced_validate_exist_user() is False:
                serializer.create_for_non_exist_user()
            user_invitee = self.get_user_invitee()
            # validate send invitation
            validate_send_invitation(organization=organization, user_invitee=user_invitee)
            # generate token invitation
            token = OrganizationService.generate_token_invitation(user=user_invitee, organization=organization,
                                                                  inviter=request.user)
            #
            url = serializer.create_url_invitation(token)
            logger.info("%s --- URL Invitation: %s", self.request.data.get('email'), url)
            org_user = serializer.adding_member(is_force_invitation=False)
            # send invitation
            serializer.send_invitation(url)
            # add invitation notification
            OrganizationService.add_invitation_notification(token=token, organization=organization, user=user_invitee,
                                                            author=self.request.user)
            #  grant default role in app Permission
            ComposePermissionService.sync_permission_of_user_client_org([str(org_user.id)])
        except Exception as error:
            raise error

        return Response({'message': 'Invitation has been sent!'},
                        status=status.HTTP_200_OK)

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()

        if message:
            # message is customized -> raise 406
            raise exceptions.NotAcceptable(detail=message)
        raise exceptions.PermissionDenied(detail=message)

    def get_permissions(self):
        self.permission_classes = (IsOrganizationAction,)
        if self.request.method == 'GET':
            return super().get_permissions()
        else:
            app_name = get_app_name_from_request(self.request)
            if app_name == APP_BUILD_TRANSIT:
                self.permission_classes = (IsOrganizationAction, LimitInternalUserPermission,)
            else:
                self.permission_classes = (IsOrganizationAction,)
        return super().get_permissions()


class ForceOrganizationUserInvitationView(OrganizationUserInvitationView):
    """Force inviting user and sending notification email"""

    serializer_class = ForceOrganizationInvitationSerializer

    def post(self, request, *args, **kwargs):
        try:
            organization = self.get_organization
            serializer = self.serializer_class(data=request.data, context={'organization': organization,
                                                                           'request': request,
                                                                           'admin': request.user,
                                                                           'app_name': self.get_app_name_profile
                                                                           })
            serializer.is_valid(raise_exception=True)
            # create new user without exist
            user_existed = serializer.advanced_validate_exist_user()
            if user_existed is False:
                serializer.create_for_non_exist_user()
            user_invitee = self.get_user_invitee()
            # validate send invitation
            validate_send_invitation(organization=organization, user_invitee=user_invitee)

            org_user = serializer.adding_member(is_force_invitation=True)
            #  grant default role in app Permission
            ComposePermissionService.sync_permission_of_user_client_org([str(org_user.id)])

            # send force invitation notice
            serializer.send_force_invite_notification(user_existed)

            # log add member activity
            data = {"Full name": f"{user_invitee.first_name} {user_invitee.last_name}", "Email": user_invitee.email}
            log_activity_task.delay(user_id=request.user.pk, action=ActivityService.action_add_member(), data=data)

        except Exception as error:
            raise error

        return Response({'message': 'Force Invitation is successfully'},
                        status=status.HTTP_200_OK)


class OrganizationTokenView(RequestLogMiddleware, APIView):
    serializer_class = OrganizationValidateTokenSerializer
    permission_classes = (AllowAny,)

    def get_token(self, request, *args, **kwargs):
        return self.kwargs.get('token', '')

    def get(self, request, *args, **kwargs):
        token = self.get_token(request)
        _verify, _status, _is_needed_changing_password = OrganizationService.get_status_invitation(token=token)
        if _verify:
            return Response({'message': 'Accepted!',
                             'status': _status,
                             'is_needed_changing_password': _is_needed_changing_password},
                            status=status.HTTP_200_OK)
        serializer = self.serializer_class(data={'token': token})
        serializer.is_valid(raise_exception=True)
        organization_user = serializer.save()
        is_needed_changing_password = serializer.is_needed_changing_password(organization_user.user)
        return Response({'message': 'Accepted!',
                         'status': None,
                         'is_needed_changing_password': is_needed_changing_password},
                        status=status.HTTP_200_OK)


class OrganizationVerifyTokenBaseView(RequestLogMiddleware, APIView):
    """
    Member accepts the invitation
    """
    serializer_class = OrganizationValidateTokenSerializer
    permission_classes = (AllowAny,)

    @abc.abstractmethod
    def get_token(self, request):
        return

    def verify_token(self, token):
        return OrganizationService.get_status_invitation(token=token)

    def processing_invitation(self, request, *args, **kwargs):
        try:
            token = self.get_token(request)
            _verify, _status, _is_needed_changing_password = self.verify_token(token)
            #
            if not _verify:
                serializer = self.serializer_class(data={'token': token})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            #
            return self.get_response(invitation_status=_status,
                                     is_needed_changing_password=_is_needed_changing_password)
        except Exception as err:
            logger.error(err)
            raise err

    def get_response(self, message='Accepted', invitation_status=None, is_needed_changing_password=False):
        return Response({'message': message,
                         'status': invitation_status,
                         'is_needed_changing_password': is_needed_changing_password},
                        status=status.HTTP_200_OK)


class OrganizationTokenGETView(OrganizationVerifyTokenBaseView):
    def get_token(self, request):
        return self.kwargs.get('token', '')

    def get(self, request, *args, **kwargs):
        """
        Verify token request with GET method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.processing_invitation(request, *args, **kwargs)


class OrganizationTokenPOSTView(OrganizationVerifyTokenBaseView):
    def get_token(self, request):
        return request.data.get('token', '')

    def post(self, request, *args, **kwargs):
        """
        Verify token request with POST method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.processing_invitation(request, *args, **kwargs)


class OrganizationUserResendInvitationView(RequestLogMiddleware, OrganizationBaseView,
                                           generics.GenericAPIView):
    serializer_class = OrganizationResendInvitationSerializer

    def post(self, request, *args, **kwargs):
        """
        Resend Invitation user to Organization
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            organization = self.get_organization
            user_invitee = self.get_user_request
            # validate user is pedding in organization
            validate_resend_invitation(organization=organization, user_invitee=user_invitee)
            # generate token invitation
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            token = OrganizationService.generate_token_invitation(user=user_invitee, organization=organization,
                                                                  inviter=request.user)
            #
            template_url = self.request.data.get('activation_link_template')
            url = template_url.replace('{token}', token)
            logger.info("%s --- URL Invitation: %s", self.request.data.get('email'), url)
            # send invitation
            app_name = self.get_app_name_profile
            EmailService.send_invitation_member_organization(user=user_invitee, url=url, organization=organization,
                                                             admin=self.request.user, app_name=app_name)
            # add invitation notification
            OrganizationService.add_invitation_notification(token=token, organization=organization, user=user_invitee,
                                                            author=self.request.user)
        except Exception as error:
            logger.error('OrganizationUserResendInvitationView', error)
            raise error

        return Response({'message': 'Invitation has been sent!'},
                        status=status.HTTP_200_OK)


class OrganizationAccessClientClientView(RequestLogMiddleware, OrganizationBaseView,
                                         generics.GenericAPIView):
    """
    Organization user access client
    """
    serializer_class = OrganizationAccessClientSerializer

    def post(self, request, *args, **kwargs):
        #
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            OrganizationRoleService.update_access_clients_for_user(organization=self.get_organization,
                                                                   user=self.get_user_request,
                                                                   client_ids=data.get('client_ids'),
                                                                   access=data.get('has_access', True))
            return Response(status=200, data={'message': 'Update status access to client success!'})
        except Exception as ex:
            raise ex


class UserInfoOrganizationClientClientView(RequestLogMiddleware, OrganizationBaseView, generics.ListAPIView):
    serializer_class = UserInfoOrganizationClientSerializer
    permission_classes = (IsAuthenticated,)

    def queryset_sort_organization(self, queryset):
        """
        filter in url with pattern &org_order_by=name,-created,...
        :param queryset:
        :return:
        """
        params = self.request.query_params.get('org_order_by', None)
        ordering = []
        if params:
            params = params.split(',')
            list_fields = [field.name for field in Organization._meta.get_fields()]
            ordering = [item for item in params if re.sub(r'[^\w]', '', item) in list_fields]
            queryset = queryset.order_by(*set(ordering))
        if not ordering:
            queryset = queryset.order_by("name")
        return queryset

    def queryset_sort_client(self, queryset):
        """
        filter in url with pattern &ws_order_by=name,-created,...
        :param queryset:
        :return:
        """
        params = self.request.query_params.get('ws_order_by', None)
        ordering = []
        if params:
            params = params.split(',')
            list_fields = [field.name for field in Client._meta.get_fields()]
            ordering = [item for item in params if re.sub(r'[^\w]', '', item) in list_fields]
            queryset = queryset.order_by(*set(ordering))
        if not ordering:
            queryset = queryset.order_by("name")
        return queryset

    def get_queryset(self):
        queryset = OrganizationService.get_organizations(user=self.request.user).distinct()
        return self.queryset_sort_organization(queryset)

    def get(self, request, *args, **kwargs):
        #
        try:
            #
            data = []
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.paginate_queryset(queryset)
            for item in queryset:
                organization_data = OrganizationSerializer(item, context={'request': request}).data
                organization_user = OrganizationRoleService.get_query_set_role_user(organization=item,
                                                                                    user=self.request.user).first()
                if not organization_user:
                    continue
                role_data = RoleSerializer(organization_user.role).data
                organization_data.update({
                    'role': role_data
                })
                query_set_client_access = UserClientService.get_query_set_access_of_user(organization=item,
                                                                                         user=self.request.user,
                                                                                         active=True)
                # Join check config app client
                query_set_client_access = AppClientConfigService.get_client_query_set_join_client_app_profile(
                    queryset=query_set_client_access)
                # order by
                query_set_client_access = self.queryset_sort_client(query_set_client_access)
                clients_serializer = OrganizationClientsModulesSerializer(query_set_client_access.all(),
                                                                          many=True,
                                                                          context={'request': request})
                temp = {
                    'organization': organization_data,
                    'clients': clients_serializer.data
                }
                data.append(temp)
            return self.get_paginated_response(data=data)
        except Exception as ex:
            raise ex


class OrganizationApprovalClientToActiveView(RequestLogMiddleware, OrganizationBaseView, generics.GenericAPIView):
    def get_serializer(self, *args, **kwargs):
        return None

    def get_client(self):
        try:
            client = Client.objects.get(pk=self.kwargs.get('client_id'))
        except Exception:
            raise InvalidParameterException(message="parameter 'client_id' is invalid.")
        if client.active:
            raise GenericException('Client have approval to active!')
        return client

    def post(self, request, *args, **kwargs):
        try:
            organization = self.get_organization
            client = self.get_client()
            OrganizationService.approval_client_to_active(organization=organization, client=client)
            return Response(status=status.HTTP_200_OK, data={'message': 'Client approval to active success'})
        except Exception as ex:
            logger.error("Organization approval client failed : {}".format(ex))
            raise ex


class OrganizationClientConfigApplication(RequestLogMiddleware, OrganizationBaseView, generics.ListAPIView):
    serializer_class = AppClientConfigSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Get list app of client user
            1. load all app from config
            2. get all app enable in db
            3. Map 1 vs 2
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            client = self.get_client()
            query_set = AppClientConfigService.get_query_set_client_app_profile(client=client, enabled=True)
            list_app_client = query_set.values_list('app', flat=True) if query_set.exists() else []
            data = []
            for app, label in LIST_APP_CONFIG:
                item = {
                    'app': app,
                    'label': label,
                    'enabled': True if app in list_app_client else False
                }
                data.append(item)
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            logger.error('Get list app client of user : {}'.format(ex))
            raise ex


class OrganizationClientConfigSwitcher(RequestLogMiddleware, OrganizationBaseView, generics.GenericAPIView):
    serializer_class = AppClientConfigSwitcherSerializer
    permission_classes = (IsAuthenticated, IsOrganizationAction)

    def post(self, request, *args, **kwargs):
        """
        Switching app profile client of user
            params : { 'enabled': True/False }
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        client = self.get_client()
        last_client = Client.objects.filter(organization_id=client.organization_id).order_by("created")[0]
        if last_client.id == last_client.id:
            raise InvalidParameterException(message="Doesn’t allow to disable the last application of a workspace")
        try:
            app = kwargs.get('app', None)
            enabled = request.data.get('enabled', True)
            if not app or app not in APP_NAME_BUILD_PROFILE:
                raise InvalidParameterException(message="App name not correct")
            AppClientConfigService.switching_client_app_profile(client=client, app=app, enabled=enabled)
            return Response(status=status.HTTP_200_OK, data=None)
        except Exception as ex:
            logger.error('Switching app client of user : {}'.format(ex))
            raise ex
