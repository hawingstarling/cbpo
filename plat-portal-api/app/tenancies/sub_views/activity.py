from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from app.core.utils import *
from app.tenancies.models import Organization, Client
from app.tenancies.permissions import IsOrganizationActivity
from app.tenancies.sub_views.organization import OrganizationBaseView
from .common import RequestLogMiddleware
from ..serializers import ActivityObjectSerializer, ActivitySerializer, ActivityActionSerializer
from ..activity_services import ActivityService

logger = logging.getLogger('django')


class ActivityBaseViewSet(RequestLogMiddleware):
    permission_classes = (IsAuthenticated,)
    serializer_class_read = ActivityObjectSerializer
    serializer_class_action = ActivityActionSerializer
    serializer_class_obj = ActivitySerializer

    def get_serializer_class(self):
        method = self.request.method if hasattr(self, 'request') else None
        args = {
            'GET': self.serializer_class_read,
            'POST': self.serializer_class_action,
            'PUT': self.serializer_class_action,
            'PATCH': self.serializer_class_action,
            'DELETE': self.serializer_class_obj,
        }
        return args.get(method, self.serializer_class_obj)

    def get_queryset(self):
        return ActivityService.get_query_set_activity()

    def normalize_data_request(self, data_info):
        data_info.update({'user': str(self.request.user.pk)})
        obj = self.get_object_data(object_type=data_info.get('object_type', None),
                                   object_id=data_info.get('object_id', None))
        data_optional = data_info.get('data', {})
        if not data_optional.get('app_profile', None):
            data_optional.update({'app_profile': get_app_name_profile()})
        if obj:
            if isinstance(obj, Client):
                data_optional.update({
                    'client_id': str(obj.pk),
                    'client_name': obj.name,
                })
            data_info.update({
                'object': str(obj.pk),
                'object_type': ContentType.objects.get_for_model(obj).pk
            })
        data_info.update({'data': data_optional})
        return data_info

    def get_object_data(self, object_type: str = None, object_id: str = None):
        if not object_type or not object_id:
            return None
        args = {
            'organization': Organization,
            'client': Client
        }
        model_class = args.get(object_type)
        try:
            obj = model_class.objects.get(id=object_id)
        except Exception as ex:
            raise ObjectNotFoundException(message="Not found object in {}".format(object_type), verbose=True)
        return obj


class ActivityListCreateViewSet(ActivityBaseViewSet, generics.ListCreateAPIView):

    def get_queryset(self):
        """
        :return:
        """
        queryset = super(ActivityListCreateViewSet, self).get_queryset()
        action = self.request.query_params.get('action', None)
        key = self.request.query_params.get('key', None)
        conditions = ActivityService.get_queryset_filter_action_object(action=action, key=key)
        queryset = queryset.filter(conditions) if conditions else queryset
        return queryset.order_by('-created')

    def post(self, request, *args, **kwargs):
        try:
            data = self.normalize_data_request(data_info=self.request.data)
            serializer = self.serializer_class_obj(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            action = data.get('action')
            if action in [ActivityService.action_access_workspace()]:
                # don't track twice
                obj_activity = data.get('object')
                if not obj_activity:
                    raise InvalidParameterException(message="Param invalid")
                find = ActivityService.get_query_set_activity(user=self.request.user, action=action,
                                                              object_id=obj_activity)
                if find.exists():
                    obj = find.first()
                    return Response(self.serializer_class_read(obj).data, status=status.HTTP_201_CREATED)
            obj = serializer.save()
            return Response(self.serializer_class_read(obj).data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            logger.error(ex)
            raise ex


class ActivityRetrieveUpdateDestroyViewSet(ActivityBaseViewSet, generics.RetrieveUpdateDestroyAPIView):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        #
        if instance is None:
            raise ObjectNotFoundException(message="Not found activity")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizationActivityListViewSet(ActivityBaseViewSet, OrganizationBaseView, generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOrganizationActivity)

    def get_serializer_class(self):
        return self.serializer_class_read

    def get_queryset(self):
        """
        :return:
        """
        queryset = super(OrganizationActivityListViewSet, self).get_queryset()
        client_ids = []
        organization = self.get_organization
        if organization:
            client_ids = Client.objects.filter(organization=organization).values_list('id', flat=True)
            client_ids = [str(item) for item in client_ids]
        action = self.request.query_params.get('action', None)
        key = self.request.query_params.get('key', None)
        if key in client_ids:
            conditions = ActivityService.get_queryset_filter_action_by_client_id(key, action)
        else:
            conditions = ActivityService.get_queryset_filter_action_object(action=action, key=key, object=Client,
                                                                           object_ids=client_ids, organization=organization)
        queryset = queryset.filter(conditions) if conditions else queryset
        return queryset.order_by('-created')


class ClientActivityListViewSet(ActivityBaseViewSet, generics.ListAPIView):
    def get_serializer_class(self):
        return self.serializer_class_read

    def get_client(self, client_id: str):
        if not client_id and isinstance(self.request.user, AnonymousUser):
            return Client.objects.none()
        try:
            client = Client.objects.get(id=client_id)
        except Exception as ex:
            raise ObjectNotFoundException(message="Not found object in Client")
        return client

    def get_queryset(self):
        """
        :return:
        """
        queryset = super(ClientActivityListViewSet, self).get_queryset()
        client = self.get_client(client_id=self.kwargs.get('pk', None))
        if client:
            action = self.request.query_params.get('action', None)
            key = self.request.query_params.get('key', None)
            conditions = ActivityService.get_queryset_filter_action_object(action=action, key=key, object=Client,
                                                                           object_ids=[str(client.pk)])
            queryset = queryset.filter(conditions) if conditions else queryset
        return queryset.order_by('-created')
