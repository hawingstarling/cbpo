import logging
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from app.core.context import AppContext
from app.financial.exceptions import CustomObjNotFoundException, ShareCustomException
from app.financial.models import ShareCustom, ClientPortal
from app.financial.permissions.base import JwtTokenPermission, ClientUserPermission
from app.financial.permissions.custom_views import ShareModePermission, CustomTypeViewPermission, \
    CustomTypeUpdatePermission, CustomTypeDeletePermission
from app.database.helper import get_connection_workspace
from app.financial.services.custom_views import CustomViewService
from app.financial.sub_serializers.custom_view_serializer import ShareCustomSerializer, ShareCustomListSerializer

logger = logging.getLogger(__name__)


class CustomBaseListCreateAPIViewSerializer(generics.ListCreateAPIView):
    serializer_class = None
    permission_classes = (ClientUserPermission,)
    custom_model = None

    featured = openapi.Parameter('featured', in_=openapi.IN_QUERY,
                                 description="""
                                Get all, featured or not featured.
                                Set 'true' to get featured objs
                                Set 'false' to get not featured objs
                                Ignore to get all objs
                                """,
                                 type=openapi.TYPE_STRING)

    type = openapi.Parameter('type', in_=openapi.IN_QUERY,
                             description="""Type get custom share by shared or myself or all""",
                             type=openapi.TYPE_STRING)

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by name of custom type""",
                               type=openapi.TYPE_STRING)

    def get_queryset_order(self, query_set: QuerySet):
        query_set = query_set.order_by('-featured', '-created')
        return query_set

    def get_queryset_extension(self, query_set: QuerySet):
        return query_set

    def get_queryset(self):
        """
        Fetch condition and make query set for custom views
        featured :
            None : get all objs of type custom
            True : get featured objs of custom type
            False: get not featured objs of custom type
        type :
            all : get all custom and share custom of type custom
            share_mode : get all objs of custom type share
            creator: get all objs of custom type
        :return:
        """
        query_params = self.request.query_params
        # featured
        featured = query_params.get("featured", None)
        # filter type

        filter_type = query_params.get("type", "all")
        # search
        search = query_params.get("search", None)
        if self.kwargs.get("user_id") is not None:
            user_id = str(self.kwargs.get("user_id"))
        else:
            user_id = AppContext.instance().user_id
        # get keyword for search
        client_db = get_connection_workspace(self.kwargs["client_id"])
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(self.custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        query_set = custom_service.get_query_set_my_custom_obj(filter_type=filter_type, search=search,
                                                               featured=featured)
        if query_set:
            query_set = self.get_queryset_order(query_set)
            query_set = self.get_queryset_extension(query_set)
        return query_set

    @swagger_auto_schema(operation_description='Get list custom type', manual_parameters=[type, search, featured])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data['user'] = str(kwargs['user_id'])
        request.data['client'] = kwargs['client_id']
        return super().post(request, *args, **kwargs)


class CustomBaseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = None
    permission_classes = [JwtTokenPermission, CustomTypeViewPermission]
    custom_model = None

    def get_queryset(self):
        query_set = self.custom_model.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    def get_permissions(self):
        if hasattr(self.request, 'method') and self.request.method.upper() in ["PUT", "PATCH"]:
            self.permission_classes = [CustomTypeUpdatePermission]
        if hasattr(self.request, 'method') and self.request.method.upper() in ["DELETE"]:
            self.permission_classes = [CustomTypeDeletePermission]
        return super().get_permissions()

    def put(self, request, *args, **kwargs):
        request.data['user'] = str(kwargs['user_id'])
        request.data['client'] = kwargs['client_id']
        return super().put(request, *args, **kwargs)


class CustomBaseListListCreateShareModeView(generics.ListCreateAPIView):
    queryset = ShareCustom.objects.all()
    serializer_class = ShareCustomSerializer
    permission_classes = [JwtTokenPermission, ShareModePermission]
    custom_model = None

    def get_queryset(self):
        client_db = get_connection_workspace(self.kwargs["client_id"])
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(self.custom_model).pk
        object_id = str(self.kwargs.get('pk')) if 'pk' in self.kwargs else None
        user_id = str(self.kwargs.get("user_id"))
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        query_set = custom_service.get_query_set_share_custom(object_id=object_id)
        if query_set:
            query_set = query_set.order_by('-created')
        return query_set

    def get_serializer_class(self):
        if hasattr(self.request, 'method') and self.request.method in SAFE_METHODS:
            self.serializer_class = ShareCustomListSerializer
        return super().get_serializer_class()

    # def get_permissions(self):
    #     if hasattr(self.request, 'method') and self.request.method in SAFE_METHODS:
    #         self.permission_classes = (JwtTokenPermission, ShareModePermission,)
    #     return super().get_permissions()

    def get_object(self):
        obj_id = str(self.kwargs.get('pk'))
        client_id = self.kwargs["client_id"]
        try:
            obj = self.custom_model.objects.tenant_db_for(client_id).get(pk=obj_id)
            return obj
        except self.custom_model.DoesNotExist:
            logger.error('Id {} not exist in {}'.format(obj_id, self.custom_model.__name__))
            raise CustomObjNotFoundException(message='Id {} not exist in {}'.format(obj_id, self.custom_model.__name__),
                                             verbose=True)

    def get_client(self):
        obj_id = str(self.kwargs.get('client_id'))
        try:
            obj = ClientPortal.objects.tenant_db_for(obj_id).get(pk=obj_id)
            return obj
        except ClientPortal.DoesNotExist:
            logger.error('Id {} not exist in Client Portal'.format(obj_id))
            raise CustomObjNotFoundException(message='Id {} not exist in Client Portal'.format(obj_id),
                                             verbose=True)

    def post(self, request, *args, **kwargs):
        serializer_class = ShareCustomSerializer(data=request.data, context={
            'request': self.request,
            'client': self.get_client()
        })
        serializer_class.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer_class.update(instance=self.get_object(), validated_data=serializer_class.validated_data)
            return Response(data=None, status=status.HTTP_200_OK)
        except Exception as ex:
            logger.error('[{}CreateShareModeView] : {}'.format(self.custom_model.__name__, str(ex)))
            raise ShareCustomException(
                message='[{}CreateShareModeView] : {}'.format(self.custom_model.__name__, str(ex)), verbose=True)
