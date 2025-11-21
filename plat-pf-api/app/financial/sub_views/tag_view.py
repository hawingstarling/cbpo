from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core.context import AppContext
from app.financial.models import TagClient
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.tag_serializer import TagSerializer, TagCreateSerializer, TagCreateBulkSerializer


class ListCreateTagView(generics.ListCreateAPIView):
    permission_classes = [JwtTokenPermission]
    queryset = TagClient.objects.all()
    serializer_class = TagSerializer

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Keyword get tags suggestion""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        base_filter = Q(client_id=client_id)
        keyword = self.request.query_params.get("keyword", None)
        if keyword is not None:
            base_filter &= Q(name__icontains=keyword)
        #
        res_query_set = TagClient.objects.tenant_db_for(client_id).filter(base_filter).order_by('name')
        return res_query_set

    @swagger_auto_schema(operation_description='List tags of clients',
                         manual_parameters=[keyword], responses={status.HTTP_200_OK: TagSerializer})
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="create tag of clients",
                         request_body=TagCreateSerializer,
                         responses={status.HTTP_201_CREATED: TagSerializer})
    def post(self, request, *args, **kwargs):
        request.data['creator'] = AppContext.instance().user_id
        request.data['client'] = kwargs['client_id']
        return super().post(request, *args, **kwargs)


class RetrieveUpdateDeleteTagView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [JwtTokenPermission]
    queryset = TagClient.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        query_set = TagClient.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    @swagger_auto_schema(operation_description="create tag of clients",
                         request_body=TagCreateSerializer,
                         responses={status.HTTP_200_OK: TagSerializer})
    def put(self, request, *args, **kwargs):
        request.data['creator'] = AppContext.instance().user_id
        request.data['client'] = kwargs['client_id']
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="create tag of clients",
                         request_body=TagCreateSerializer,
                         responses={status.HTTP_200_OK: TagSerializer})
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ClientTagsBulkView(APIView):

    @swagger_auto_schema(operation_description="bulk assign tags for custom views",
                         request_body=TagCreateBulkSerializer,
                         responses={status.HTTP_201_CREATED: None})
    def post(self, request, *args, **kwargs):
        serializer = TagCreateBulkSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        serializer.bulk_update(validated_data)

        return Response(status=status.HTTP_200_OK)
