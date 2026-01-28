from typing import Union
import uuid
import maya
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.generics import GenericAPIView, get_object_or_404

from ..models import DataImportTemporary
from ..services.utils.utils import load_lib_module
from ..sub_serializers.lib_import_serializer import LibImportModelSerializer, ImportHistorySerializer


class GenericImportView(GenericAPIView):
    serializer_class = LibImportModelSerializer
    queryset = DataImportTemporary.objects.all()

    def get_object(self):
        pk = self.kwargs.get('import_id')
        module = self.kwargs.get('module')
        queryset = DataImportTemporary.objects.filter(pk=pk, module=module)
        return get_object_or_404(queryset)

    @property
    def lib_module(self):
        module = self.kwargs['module']
        return load_lib_module(module)

    def validate(self):
        self.lib_module.validate_request_api_view(self.request, *self.args, **self.kwargs)

    def get_permissions(self):
        self.validate()
        self.permission_classes = self.lib_module.permissions_class
        return super().get_permissions()


class ListImportHistoryView(generics.ListAPIView):
    serializer_class = ImportHistorySerializer
    queryset = DataImportTemporary.objects.all()

    module = openapi.Parameter('module', in_=openapi.IN_QUERY,
                               description="""Filter module""",
                               type=openapi.TYPE_STRING)
    status = openapi.Parameter('status', in_=openapi.IN_QUERY,
                               description="""Filter status""",
                               type=openapi.TYPE_STRING)
    import_id = openapi.Parameter('import_id', in_=openapi.IN_QUERY,
                                  description="""Filter import_id""",
                                  type=openapi.TYPE_STRING)
    from_date = openapi.Parameter('from_date', in_=openapi.IN_QUERY,
                                  description="""Filter from_date""",
                                  type=openapi.TYPE_STRING)
    to_date = openapi.Parameter('to_date', in_=openapi.IN_QUERY,
                                description="""Filter to_date""",
                                type=openapi.TYPE_STRING)
    username = openapi.Parameter('username', in_=openapi.IN_QUERY,
                                 description="""Filter username""",
                                 type=openapi.TYPE_STRING)
    file_name = openapi.Parameter('file_name', in_=openapi.IN_QUERY,
                                  description="""Filter file_name""",
                                  type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='List import history',
                         manual_parameters=[module, status, import_id, from_date, to_date, username, file_name])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        client_id = self.kwargs.get("client_id", None)
        base_filter = Q(client_id=client_id) if client_id else Q()

        _filter = self.__get_filter_params(self.request.query_params)
        if _filter:
            base_filter.add(_filter, Q.AND)
        return DataImportTemporary.objects.filter(base_filter).order_by("-created")

    @classmethod
    def __get_filter_params(cls, query_params: any) -> Union[Q, None]:
        _filter = Q()

        if query_params.get("module", None):
            _filter.add(Q(module=query_params["module"]), Q.AND)

        if query_params.get("status", None):
            _filter.add(Q(status=query_params["status"]), Q.AND)

        if query_params.get("import_id", None):
            _filter.add(Q(id=query_params["import_id"]), Q.AND)

        from_date = query_params.get('from_date')
        to_date = query_params.get('to_date')

        if from_date:
            from_date = maya.parse(from_date).datetime().date()
            _filter.add(Q(created__date__gte=from_date), Q.AND)
        if to_date:
            to_date = maya.parse(to_date).datetime().date()
            _filter.add(Q(created__date__lte=to_date), Q.AND)

        if query_params.get("username", None):
            _filter.add(Q(meta__username__icontains=query_params["username"]), Q.AND)

        if query_params.get("file_name", None):
            _filter.add(Q(meta__file_name__icontains=query_params["file_name"]), Q.AND)

        if query_params.get("keyword", None):
            keyword_filter = Q()
            try:
                import_id = uuid.UUID(query_params["keyword"])
                keyword_filter.add(Q(id=import_id), Q.OR)
            except ValueError:
                pass
            keyword_filter.add(Q(meta__username__icontains=query_params["keyword"]), Q.OR)
            keyword_filter.add(Q(meta__file_name__icontains=query_params["keyword"]), Q.OR)
            _filter.add(keyword_filter, Q.AND)

        return None if _filter == {} else _filter
