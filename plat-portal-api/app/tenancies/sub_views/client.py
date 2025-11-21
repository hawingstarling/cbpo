import abc
import re
from typing import List
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from firebase_admin.firestore import client
from rest_framework import generics, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from app.core.simple_authentication import get_app_name_from_request
from app.core.logger import logger
from app.core.utils import *
from app.tenancies.config_static_variable import MODULE_ENUM, MEMBER_STATUS
from app.tenancies.models import (
    User,
    Client,
    UserClient,
    ClientModule, OrganizationUser,
)
from app.tenancies.permissions import (
    IsAdminManagerOrReadOnlyClient,
    IsAdminManagerClientModule,
    IsAdminManagerClientModuleOrMyself,
    UserCanCreateClient,
    IsOrganizationManagerClientModule,
    LimitExternalUserPermission,
)
from app.tenancies.serializers import (
    ClientSerializer,
    ClientModulesSerializer,
    UserClientSerializer,
    ClientInvitationSerializer,
    UserClientListSerializer,
    UserClientSettingDataSerializer,
    CustomRefreshJSONWebTokenSerializer,
    UpdateRoleUserClientSerializer,
    UserSerializer,
    ClientModulesInternalSerializer,
    ClientInfoInternalSerializer,
    ForceClientInvitationSerializer, ClientStatusInfoInternalSerializer,
)
from app.tenancies.services import RoleService, ClientService, OrganizationService
from .common import AppBaseView
from .common import RequestLogMiddleware
from ..config_app_and_module import APP_BUILD_TRANSIT
from ..observer.publisher import publisher
from ..permissions_internal_services import IsInternalServices
from ..activity_services import ActivityService
from app.tenancies.tasks import log_activity_task


class ClientUserBelongView(RequestLogMiddleware, generics.ListAPIView):
    """
    List all clients that user belongs to
    """

    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        client_ids = UserClient.objects.filter(
            user=user, status=MEMBER_STATUS[0][0]
        ).values_list("client_id", flat=True)
        queryset = Client.objects.filter(id__in=client_ids).all().order_by("pk")
        return queryset


class ClientRegisterView(RequestLogMiddleware, generics.CreateAPIView):
    """
    Register new Client
    """

    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated, UserCanCreateClient)


class ClientBaseView(AppBaseView):
    serializer_class = ClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminManagerOrReadOnlyClient,
    )

    def get_user(self):
        return self.request.user

    def get_client(self):
        if not self.kwargs.get("pk", None) and not self.kwargs.get("client_id", None):
            return None
        try:
            pk = (
                self.kwargs.get("pk")
                if self.kwargs.get("pk", None)
                else self.kwargs.get("client_id")
            )
            client = Client.objects.get(pk=pk)
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")
        return client


class ClientInformationView(
    RequestLogMiddleware, ClientBaseView, generics.RetrieveUpdateAPIView
):
    """
    View or Update Client Information
    """

    queryset = Client.objects.all()


class ClientModulesView(RequestLogMiddleware, ClientBaseView, generics.ListAPIView):
    """
    View list modules of Client
    """

    serializer_class = ClientModulesSerializer

    def get_queryset(self):
        client = self.get_client()
        queryset = (
            ClientModule.objects.filter(
                client=client, module__in=self.get_modules_app_profiles
            )
            .all()
            .order_by("module")
        )
        return queryset


class ModuleSwitchingStatusView(
    RequestLogMiddleware, ClientBaseView, generics.UpdateAPIView
):
    """
    Switch status of the specific Client's module
    """

    serializer_class = ClientModulesSerializer
    permission_classes = (
        IsAuthenticated,
        IsOrganizationManagerClientModule,
    )

    def get_module(self):
        if self.kwargs.get("module") not in dict(MODULE_ENUM).keys():
            raise InvalidParameterException(message="parameter 'module' is invalid")
        return self.kwargs.get("module")

    def get_object(self):
        client = self.get_client()
        module = self.get_module()
        client_module = ClientModule.objects.filter(
            client=client, module=module
        ).first()
        #
        #
        publisher.notify(
            # push firebase, redis
            event_type="UPDATE_WORKSPACE_MODULE",
            client_id=client.id
        )
        return client_module


class UserClientListView(RequestLogMiddleware, ClientBaseView, generics.ListAPIView):
    """
    List all users of the client
    """

    serializer_class = UserClientListSerializer

    def get_queryset(self):
        client = self.get_client()
        is_external_user_request = self._is_external_user_request(self.request.user, client)
        if is_external_user_request:
            # in case of external user's request
            # return a list of limited users who are in WS only
            queryset = UserClient.objects.filter(
                client=client, user__user_id__in=self._get_list_external_user_ids(client))
        else:
            queryset = UserClient.objects.filter(client=client)

        roles = self.request.GET.getlist("roles[]", [])
        key = self.request.query_params.get("key", None)
        if roles:
            roles = [re.sub(r"[^\w]", "", item).upper() for item in roles]
            queryset = queryset.filter(role__key__in=roles)
        if key:
            conditions = (
                    Q(user__username__icontains=key)
                    | Q(user__email__contains=key)
                    | Q(user__first_name__icontains=key)
                    | Q(user__last_name__icontains=key)
            )
            queryset = queryset.filter(conditions)
        return queryset.order_by("created")

    @classmethod
    def _get_list_external_user_ids(cls, client) -> List[UUID]:
        return OrganizationUser.objects.filter(
            organization_id=client.organization_id, role__key="CLIENT").values_list("user_id", flat=True)

    @classmethod
    def _is_external_user_request(cls, user: User, client: Client) -> bool:
        try:
            org_user = OrganizationUser.objects.get(organization_id=client.organization_id, user__user_id=user.user_id)
        except Exception as err:
            logger.error(err)
            raise err
        return org_user.is_external_user


class ClientVerifyTokenBaseView(RequestLogMiddleware, APIView):
    """
    Member accepts the invitation
    """

    permission_classes = (AllowAny,)

    @abc.abstractmethod
    def get_token(self, request):
        return

    def verify_token(self, token):
        (
            _verify,
            _status,
            _is_needed_changing_password,
        ) = ClientService.get_status_invitation(token=token)
        return _verify, _status, _is_needed_changing_password

    def get_response(
            self,
            message="Accepted",
            invitation_status=None,
            is_needed_changing_password=False,
    ):
        return Response(
            {
                "message": message,
                "status": invitation_status,
                "is_needed_changing_password": is_needed_changing_password,
            },
            status=status.HTTP_200_OK,
        )


# class ClientMemberAcceptingView(RequestLogMiddleware, APIView):
#     """
#     Member accepts the invitation
#     """
#     serializer_class = UserClientSerializer
#     permission_classes = (AllowAny,)
#
#     def get_token(self, request, *args, **kwargs):
#         return self.kwargs.get('token', '')
#
#     def get(self, request, *args, **kwargs):
#         #
#         token = self.get_token(request)
#         _verify, _status, _is_needed_changing_password = ClientService.get_status_invitation(token=token)
#         if _verify:
#             return Response({'message': 'Accepted!',
#                              'status': _status,
#                              'is_needed_changing_password': _is_needed_changing_password},
#                             status=status.HTTP_200_OK)
#         #
#         serializer = self.serializer_class(data={'token': self.get_token(request)})
#         serializer.is_valid(raise_exception=True)
#         client_user = serializer.save()
#         is_needed_changing_password = serializer.is_needed_changing_password(client_user.user)
#         return Response({'message': 'Accepted!',
#                          'status': None,
#                          'is_needed_changing_password': is_needed_changing_password},
#                         status=status.HTTP_200_OK)


class ClientMemberAcceptingGETView(ClientVerifyTokenBaseView):
    """
    GET version
    Member accepts the invitation
    """

    serializer_class = UserClientSerializer

    def get_token(self, request):
        return self.kwargs.get("token", "")

    def get(self, request, *args, **kwargs):
        try:
            token = self.get_token(request)
            _verify, _status, _is_needed_changing_password = self.verify_token(token)
            if _verify:
                return self.get_response(
                    invitation_status=_status,
                    is_needed_changing_password=_is_needed_changing_password,
                )
            #
            serializer = self.serializer_class(data={"token": token})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            #
            return self.get_response(
                invitation_status=_status,
                is_needed_changing_password=_is_needed_changing_password,
            )
        except Exception as err:
            logger.error(err)
            raise err


class ClientMemberAcceptingPOSTView(ClientVerifyTokenBaseView):
    """
    POST version
    Member accepts the invitation
    """

    serializer_class = UserClientSerializer

    def get_token(self, request):
        token = request.data.get("token")
        return token

    def post(self, request, *args, **kwargs):
        try:
            token = self.get_token(request)
            _verify, _status, _is_needed_changing_password = self.verify_token(token)
            #
            serializer = self.serializer_class(data={"token": token})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            #
            return self.get_response(
                invitation_status=_status,
                is_needed_changing_password=_is_needed_changing_password,
            )
        except Exception as err:
            logger.error(err)
            raise err


class ClientInvitationView(
    RequestLogMiddleware, ClientBaseView, generics.GenericAPIView
):
    """
    Invite new member by email
    """

    serializer_class = ClientInvitationSerializer

    def post(self, request, *args, **kwargs):
        try:
            client = self.get_client()
            serializer = self.serializer_class(
                data=request.data,
                context={"client": client, "request": request, "admin": request.user,
                         "app_name": self.get_app_name_profile},
            )
            serializer.is_valid(raise_exception=True)
            #
            if serializer.advanced_validate_exist_user() is False:
                serializer.create_for_non_exist_user()
            user_client_organization = False
            user = self.get_user_invitee()
            #
            find_user_organization = OrganizationService.query_set_member_organization(
                user=user, organization=client.organization
            )
            if not find_user_organization.exists():
                user_client_organization = True
            #
            token = ClientService.generate_token_invitation(user, client, inviter=request.user)
            url = serializer.create_url_invitation(token)
            logger.info(
                "%s --- URL Invitation: %s", self.request.data.get("email"), url
            )
            serializer.adding_member(
                user_client_organization=user_client_organization,
                is_force_invitation=False,
            )
            serializer.send_invitation(url)
            serializer.add_invitation_notification(token)
        except Exception as error:
            logger.error(error)
            raise error

        return Response(
            {"message": "Invitation has been sent!"}, status=status.HTTP_200_OK
        )

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

    def get_user_invitee(self):
        email = self.request.data.get("email", None).lower()
        try:
            return User.objects.filter(email=email).first()
        except User.DoesNotExist:
            logger.debug("Get USer Invitation Organization Error : {}".format(email))
            raise ObjectNotFoundException("Email invitation not correct!")

    def get_permissions(self):
        self.permission_classes = (IsAdminManagerClientModule,)
        if self.request.method == "GET":
            return super().get_permissions()
        else:
            app_name = get_app_name_from_request(self.request)
            if app_name == APP_BUILD_TRANSIT:
                self.permission_classes = (
                    IsAdminManagerClientModule,
                    LimitExternalUserPermission,
                )
            else:
                self.permission_classes = (IsAdminManagerClientModule,)
        return super().get_permissions()


class ForceClientInvitationView(ClientInvitationView):
    """Force inviting user and sending notification email"""

    serializer_class = ForceClientInvitationSerializer

    def post(self, request, *args, **kwargs):
        try:
            client = self.get_client()
            serializer = self.serializer_class(
                data=request.data,
                context={"client": client, "request": request, "admin": request.user,
                         "app_name": self.get_app_name_profile},
            )
            serializer.is_valid(raise_exception=True)
            #
            user_existed = serializer.advanced_validate_exist_user()
            if user_existed is False:
                serializer.create_for_non_exist_user()
            user_client_organization = False
            user = self.get_user_invitee()
            #
            find_user_organization = OrganizationService.query_set_member_organization(
                user=user, organization=client.organization
            )

            if not find_user_organization.exists():
                user_client_organization = True

            serializer.adding_member(
                user_client_organization=user_client_organization,
                is_force_invitation=True,
            )
            # send force invitation notice
            serializer.send_force_invite_notification(user_existed)

            # log add member activity
            data = {"Full name": f"{user.first_name} {user.last_name}", "Email": user.email}
            log_activity_task.delay(user_id=request.user.pk, action=ActivityService.action_add_member(), data=data)

        except Exception as error:
            logger.error(error)
            raise error

        return Response(
            {"message": "Force Invitation is successful!"}, status=status.HTTP_200_OK
        )


class ClientDeleteInvitationView(
    RequestLogMiddleware, ClientBaseView, generics.DestroyAPIView
):
    """
    Delete Pending Member by user_client_id
    """

    serializer_class = UserClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminManagerClientModule,
    )

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs.get("user_id"))
        except Exception:
            raise InvalidParameterException(message="parameter 'user_id' is invalid.")

    def get_object(self):
        client = self.get_client()
        user = self.get_user()
        try:
            user_client = UserClient.objects.get(client=client, user=user)
            if user_client.is_pending() is True:
                return user_client
            return None
        except Exception:
            raise InvalidParameterException(message="parameter is invalid.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            raise StatusConflictException()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientDeleteMemberView(
    RequestLogMiddleware, ClientBaseView, generics.DestroyAPIView
):
    """
    Delete member in Client by user_client_id
    """

    serializer_class = UserClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminManagerClientModule,
    )

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs.get("user_id"))
        except Exception:
            raise InvalidParameterException(message="parameter 'user_id' is invalid.")

    def get_object(self):
        client = self.get_client()
        user = self.get_user()
        try:
            user_client = UserClient.objects.get(client=client, user=user)
            if not user_client.is_owner():
                return user_client
            return None
        except Exception:
            raise InvalidParameterException(message="parameter is invalid.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #
        if instance is None:
            raise OwnerRoleUpdateException()
        self.perform_destroy(instance)

        # Log delete member activity
        data = {"Full name": f"{instance.user.first_name} {instance.user.last_name}",
                "Email": instance.user.email,
                "Workspace": instance.client.name
                }
        log_activity_task.delay(user_id=request.user.pk, action=ActivityService.action_delete_member(), data=data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserClientSettingDataView(
    RequestLogMiddleware, ClientBaseView, generics.RetrieveAPIView
):
    """
    Get Member Client's Settings
    """

    permission_classes = (IsAuthenticated, IsAdminManagerClientModuleOrMyself)
    serializer_class = UserClientSettingDataSerializer

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs.get("user_id"))
        except Exception:
            raise InvalidParameterException(message="parameter 'user_id' is invalid.")

    def get_object(self):
        client = self.get_client()
        user = self.get_user()
        try:
            return UserClient.objects.get(user=user, client=client)
        except Exception:
            raise InvalidParameterException(message="parameter is invalid.")


class UserAllClientSettingDataView(RequestLogMiddleware, generics.ListAPIView):
    """
    Get Member Client's Settings for ALL Client
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserClientSettingDataSerializer

    def get_queryset(self):
        queryset = (
            UserClient.objects.filter(user=self.request.user).all().order_by("created")
        )
        return queryset


class CustomRefreshJSONWebToken(RequestLogMiddleware, TokenRefreshView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token
    If 'orig_iat' field (original issued-at-time) is found, will first check
    if it's within expiration window, then copy it to the new token
    """

    serializer_class = CustomRefreshJSONWebTokenSerializer


class UpdateRoleView(RequestLogMiddleware, ClientBaseView, generics.UpdateAPIView):
    """
    :body: role_update
        available = [admin, staff]
    """

    serializer_class = UpdateRoleUserClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminManagerClientModule,
    )

    def get_user(self):
        try:
            return User.objects.get(pk=self.kwargs.get("user_id"))
        except Exception:
            raise InvalidParameterException(message="parameter 'user_id' is invalid.")

    def get_object(self):
        client = self.get_client()
        user = self.get_user()
        try:
            return UserClient.objects.get(client=client, user=user)
        except Exception:
            raise InvalidParameterException(message="parameter is invalid.")

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        role_name = serializer.validated_data.get("role_update")
        serializer.update(obj, role_name)

        return Response({"message": "Role updated"})


class UsersSuggestionForInvitation(
    RequestLogMiddleware, ClientBaseView, generics.ListAPIView
):
    """
    GET list user suggest from another work spaces in invitational page.
    ---
        parameters:
            - name: key
                description: optional typing email
            - name: limit
                description: optional limit
    """

    serializer_class = UserSerializer
    permission_classes = (
        IsAuthenticated,
        IsAdminManagerClientModule,
    )

    def get_queryset(self):
        client_ids = self.get_managed_by_me_client_ids()
        key = self.request.GET.get("key", None)
        if key:
            unique_user_ids = (
                UserClient.objects.filter(
                    client_id__in=client_ids,
                    status=MEMBER_STATUS[0][0],
                    user__email__contains=key,
                )
                .all()
                .order_by("-created")
                .values_list("user_id", flat=True)
            )

        else:
            unique_user_ids = (
                UserClient.objects.filter(
                    client_id__in=client_ids, status=MEMBER_STATUS[0][0]
                )
                .all()
                .order_by("-created")
                .values_list("user_id", flat=True)
            )

        unique_user_ids = list(set(unique_user_ids))
        # remove user_id who is taking the action
        unique_user_ids = [i for i in unique_user_ids]
        if self.request.user.pk in unique_user_ids:
            unique_user_ids.remove(self.request.user.pk)

        queryset = User.objects.filter(user_id__in=unique_user_ids).order_by("created")

        queryset_limit = self.request.GET.get("limit", 10)
        return queryset[: int(queryset_limit)]

    def get_managed_by_me_client_ids(self):
        """
        GET list client id (another workspaces)
        that user belongs as admin role or higher
        :return:
        """
        user = self.request.user
        owner = RoleService.role_owner()
        admin = RoleService.role_admin()
        client_ids = UserClient.objects.filter(
            user=user, status=MEMBER_STATUS[0][0], role=owner
        ).values_list("client_id", flat=True) | UserClient.objects.filter(
            user=user, status=MEMBER_STATUS[0][0], role=admin
        ).order_by(
            "-created"
        ).values_list(
            "client_id", flat=True
        )
        final_client_ids = []
        [final_client_ids.append(str(i)) for i in client_ids]
        # ignore the current client
        final_client_ids.remove(str(self.kwargs.get("client_id")))
        return final_client_ids


class ClientModelInternalGetView(RequestLogMiddleware, ClientBaseView, APIView):
    """
    Switch status of the specific Client's module
    """

    permission_classes = (AllowAny,)

    def get_client_ip(self):
        try:
            x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = self.request.META.get("REMOTE_ADDR")
            return ip
        except Exception as ex:
            return "not found"

    def get_module(self):
        if self.kwargs.get("module") not in dict(MODULE_ENUM).keys():
            raise InvalidParameterException(message="parameter 'module' is invalid")
        return self.kwargs.get("module")

    def get_object(self):
        client = self.get_client()
        module = self.get_module()
        client_module = ClientModule.objects.filter(
            client=client, module=module
        ).first()
        return client_module

    def get(self, request, *args, **kwargs):
        ip_address = self.get_client_ip()
        try:
            logger.info("[ClientModelInternalGetView] IP address {}".format(ip_address))
            client = self.get_client()
            obj = self.get_object()
            client_data = ClientInfoInternalSerializer(client).data
            if not obj:
                obj = {"module": self.kwargs["module"], "enabled": False}
            module_data = ClientModulesInternalSerializer(obj).data
            data = {"client": client_data, **module_data}
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            logger.error(
                "[ClientModelInternalGetView] IP Address [{}] {}".format(
                    ip_address, str(ex)
                )
            )
            raise ex


class ClientStatusInternalGetView(ClientModelInternalGetView):
    """
    Switch status of the specific Client's module
    """

    permission_classes = [IsInternalServices]

    def perform_authentication(self, request):
        pass

    def get_client_ip(self):
        try:
            x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = self.request.META.get("REMOTE_ADDR")
            return ip
        except Exception as ex:
            return "not found"

    def get_object(self):
        try:
            client_id = self.kwargs["pk"]
            client = Client.all_objects.get(pk=client_id)
        except Exception:
            raise InvalidParameterException(message="parameter 'pk' is invalid.")
        return client

    @swagger_auto_schema(
        tags=["Internally"],
        operation_description="This is endpoint for using check internal that workspace is active or deactivate"
    )
    def get(self, request, *args, **kwargs):
        ip_address = self.get_client_ip()
        try:
            logger.info(f"[{self.__class__.__name__}] IP address {ip_address}")
            data = ClientStatusInfoInternalSerializer(self.get_object()).data
            return Response(status=status.HTTP_200_OK, data=data)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}] IP Address [{ip_address}] {ex}"
            )
            raise ex


class UserClientTrackLogin(RequestLogMiddleware, APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=None,
        operation_summary="User Client Track Active",
        operation_description="This endpoint does not require a request body."
    )
    def post(self, request, *args, **kwargs):
        time_now = timezone.now()
        user = request.user
        client_obj = get_object_or_404(Client, pk=self.kwargs.get("client_id"))
        client_user = UserClient.objects.get(user=user, client=client_obj)
        if client_user.last_active is None or client_user.last_active.day != time_now.day:
            client_user.last_active = time_now
            client_user.save(update_fields=["last_active"])
        org_user = OrganizationUser.objects.get(user=user, organization=client_obj.organization)
        if org_user.last_active is None or org_user.last_active.day != time_now.day:
            org_user.last_active = time_now
            org_user.save(update_fields=["last_active"])
        return Response(status=200)
