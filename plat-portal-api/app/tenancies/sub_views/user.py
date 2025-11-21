from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from app.core.logger import logger
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.core.exceptions import InvalidParameterException
from ..serializers import (ClientSerializer, AllUserClientSettingDataSerializer, NotificationSerializer)
from ..models import Client, User, UserClient, Notification
from ..permissions import (UserUpdateNotificationPermission)
from ..config_static_variable import (MEMBER_STATUS, NOTIFICATION_STATUS)
from .common import RequestLogMiddleware, AppBaseView


class ClientUserBelongView(RequestLogMiddleware, generics.ListAPIView):
    """
    List all clients that user belongs to
    """
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        client_ids = UserClient.objects.filter(
            user=user, status=MEMBER_STATUS[0][0]).values_list('client_id', flat=True)
        queryset = Client.objects.filter(id__in=client_ids).all().order_by('pk')
        return queryset


class NumberNewNotificationView(RequestLogMiddleware, APIView):
    """
    Get the number of new notification that is not seen for a user
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            count = Notification.objects.filter(user=self.request.user, is_seen=False).count()
            return Response({'count': count})
        except Exception as err:
            logger.exception('NumberNewNotificationView', err)
            raise err


class ListNotificationView(RequestLogMiddleware, generics.ListAPIView):
    """
    Get list notification sorted by created time
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        try:
            query = Notification.objects.filter(user=self.request.user).order_by('-created').all()
            return query
        except Exception as err:
            logger.exception('ListNotificationView', err)
            raise err


class UpdateNotificationIsSeenView(RequestLogMiddleware, APIView):
    """
    Retrieve and update a notification is_seen
    """
    permission_classes = (IsAuthenticated, UserUpdateNotificationPermission)
    serializer_class = NotificationSerializer

    def get_object(self):
        try:
            notification_id = self.kwargs.get('notification_id')
            notification = Notification.objects.get(pk=notification_id)
            return notification
        except ImportError:
            raise InvalidParameterException(message="parameter 'notification_id' is invalid.")

    def put(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            notification.is_seen = True
            notification.save()
            serializer = self.serializer_class(notification)
            data = serializer.data
        except Exception as err:
            logger.exception('UpdateNotificationStatusView', err)
            raise err

        return Response(data)


class UpdateNotificationIsSeenDeclineView(UpdateNotificationIsSeenView):
    """
        Update a notification is_seen decline
        """

    def put(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            notification.is_seen = True
            notification.meta.update({'action': 'Decline'})
            notification.save()
            serializer = self.serializer_class(notification)
            data = serializer.data
        except Exception as err:
            logger.exception('UpdateNotificationStatusView', err)
            raise err

        return Response(data)


class UpdateNotificationStatusView(UpdateNotificationIsSeenView):
    """
    Retrieve and update a notification status
    """

    def put(self, request, *args, **kwargs):
        try:
            notification = self.get_object()
            notification.status = NOTIFICATION_STATUS[1][0]  # DONE
            notification.save()
            serializer = self.serializer_class(notification)
            data = serializer.data
        except Exception as err:
            logger.exception('UpdateNotificationStatusView', err)
            raise err

        return Response(data)


class UserAllClientSettingDataView(RequestLogMiddleware, AppBaseView, generics.ListAPIView):
    """
    Get Member Client's Settings for ALL Client
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AllUserClientSettingDataSerializer

    def get_queryset(self):
        queryset = UserClient.objects.filter(user=self.request.user,
                                             status=MEMBER_STATUS[0][0],
                                             client__clientmodule__module__in=self.get_modules_app_profiles,
                                             client__is_removed=False).distinct().all().order_by('created')
        return queryset


class CheckUserExistedView(RequestLogMiddleware, APIView):
    permission_classes = (IsAuthenticated,)

    """
    Check user is existed in system by email
    """

    email = openapi.Parameter(
        "email",
        in_=openapi.IN_QUERY,
        description="""check by email""",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[email])
    def get(self, request, *args, **kwargs):
        status_code = status.HTTP_200_OK
        try:
            email = request.query_params.get('email')
            User.objects.get(email=email)
            return Response(status=200)
        except User.DoesNotExist:
            status_code = status.HTTP_404_NOT_FOUND
        return Response(status=status_code)
 