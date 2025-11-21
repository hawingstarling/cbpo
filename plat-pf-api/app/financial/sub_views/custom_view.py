import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, QuerySet
from django.db.models.functions import Coalesce
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from app.financial.models import CustomView, TagView, TagClient
from app.financial.sub_views.base_view import CustomBaseListCreateAPIViewSerializer, \
    CustomBaseListListCreateShareModeView, \
    CustomBaseRetrieveUpdateDestroyView
from ..services.custom_views import CustomViewService
from ..sub_serializers.custom_view_serializer import CustomViewSerializer, CustomViewCreateSerializer, \
    CustomViewTagFiltersSerializer, ClientTagViewSerializer, ClientTagViewWidgetPayloadSerializer, \
    ClientTagUserSerializer, CustomViewDropdownSerializer
from ..sub_serializers.tag_serializer import TagSerializer
from ...core.context import AppContext
from ...core.exceptions import InvalidParameterException
from ...database.helper import get_connection_workspace

logger = logging.getLogger(__name__)


class CustomViewListCreateView(CustomBaseListCreateAPIViewSerializer):
    serializer_class = CustomViewSerializer
    custom_model = CustomView

    tag = openapi.Parameter('tag', in_=openapi.IN_QUERY,
                            description="""Search by tag of custom view""",
                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description="create custom report profile for filter data source",
                         request_body=CustomViewCreateSerializer,
                         responses={status.HTTP_201_CREATED: CustomViewSerializer})
    def get_queryset_extension(self, query_set: QuerySet):
        tag = self.request.query_params.get("tag")
        if tag:
            query_set = query_set.filter(tagview__tag__name=tag)
        return query_set

    @swagger_auto_schema(operation_description='Get list custom view',
                         manual_parameters=[CustomBaseListCreateAPIViewSerializer.type,
                                            CustomBaseListCreateAPIViewSerializer.search,
                                            CustomBaseListCreateAPIViewSerializer.featured,
                                            tag])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomViewListDropdownView(generics.ListAPIView):
    serializer_class = CustomViewDropdownSerializer
    custom_model = CustomView

    def get_queryset(self):
        query_params = self.request.query_params
        # search
        user_id = AppContext.instance().user_id
        filter_type = 'all'
        # get keyword for search
        client_db = get_connection_workspace(self.kwargs["client_id"])
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(self.custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        query_set = custom_service.get_query_set_my_custom_obj(filter_type=filter_type,
                                                               search=query_params.get("search", None),
                                                               is_load_favorites=False)
        if query_set:
            query_set = query_set.order_by('name')
        return query_set

    @swagger_auto_schema(operation_description='Get list custom view dropdown',
                         manual_parameters=[CustomBaseListCreateAPIViewSerializer.search])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomViewTagFilterView(generics.RetrieveAPIView):
    serializer_class = CustomViewTagFiltersSerializer
    custom_model = CustomView
    tag = openapi.Parameter('tag', in_=openapi.IN_QUERY, description="""Tag get filter""", type=openapi.TYPE_STRING)

    def get_queryset(self):
        tag = self.request.query_params.get('tag', None)
        assert tag is not None, "Tag name is not empty"
        filter_type = 'all'
        user_id = AppContext.instance().user_id
        client_db = get_connection_workspace(self.kwargs["client_id"])
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(self.custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        query_set = custom_service.get_query_set_my_custom_obj(filter_type=filter_type, is_load_favorites=False)
        queryset = query_set.filter(tagview__tag__name=tag)
        return queryset

    @swagger_auto_schema(operation_description='Get tags filter',
                         manual_parameters=[tag], responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.count() == 0:
            raise InvalidParameterException(f"Not found records have tag {self.request.query_params.get('tag')}")
        data = CustomViewTagFiltersSerializer(queryset, many=True).data
        return Response(status=HTTP_200_OK, data=data)


class ClientTagViewSuggestion(generics.RetrieveAPIView):
    serializer_class = ClientTagViewSerializer
    queryset = TagView

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Keyword get tags suggestion""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword", None)
        return TagView.get_queryset_popular(client_id=self.kwargs['client_id'], tag=keyword)

    @swagger_auto_schema(operation_description='Search tags suggestions',
                         manual_parameters=[keyword], responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = queryset.values_list('tag__name', flat=True).distinct()
        return Response(status=HTTP_200_OK, data=data)


class ClientTagViewAccess(APIView):
    serializer_class = ClientTagViewSerializer
    custom_model = CustomView
    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Keyword get tags user access""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword", None)
        #
        user_id = AppContext.instance().user_id
        client_db = get_connection_workspace(self.kwargs["client_id"])
        content_type_id = ContentType.objects.db_manager(using=client_db).get_for_model(self.custom_model).pk
        custom_service = CustomViewService(content_type_id=content_type_id, user_id=user_id)
        query_set = custom_service.get_query_set_my_custom_obj(filter_type='all')
        #
        query_set = query_set.filter(tagview__isnull=False)
        if keyword:
            query_set = query_set.filter(tagview__tag__icontains=keyword)
        return query_set

    @swagger_auto_schema(operation_description='Search tags user access',
                         manual_parameters=[keyword], responses={status.HTTP_200_OK: TagSerializer})
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        if queryset.count() > 0:
            client_id = self.kwargs["client_id"]
            tag_ids = list(queryset.values_list('tagview__tag__id', flat=True))
            data = TagClient.objects.tenant_db_for(client_id).filter(id__in=tag_ids) \
                .order_by('name') \
                .annotate(tag_id=F('id'),
                          tag_name=F('name'),
                          tag_color=F('color'),
                          is_widget_default=Coalesce(F('tagusertrack__is_widget_default'), False)) \
                .values('tag_id', 'tag_name', 'tag_color', 'is_widget_default')
        return Response(status=HTTP_200_OK, data=data)

    @swagger_auto_schema(
        operation_description='Update tags widget display, using child tags ["all"] if update for all tags',
        request_body=ClientTagViewWidgetPayloadSerializer, responses={status.HTTP_200_OK: None})
    def post(self, request, *args, **kwargs):
        serializer = ClientTagViewWidgetPayloadSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        #
        ClientTagUserSerializer().bulk_sync(validated_data["tags"])
        return Response(status=HTTP_200_OK)


class CustomViewRetrieveUpdateDestroyView(CustomBaseRetrieveUpdateDestroyView):
    queryset = CustomView.objects.all()
    serializer_class = CustomViewSerializer
    custom_model = CustomView


class CustomViewListCreateShareModeView(CustomBaseListListCreateShareModeView):
    custom_model = CustomView
