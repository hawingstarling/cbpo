from plat_import_lib_api.services.utils.utils import load_lib_module

from plat_import_lib_api.services.controllers.module import ModuleImportService

from ..sub_serializers.lib_import_serializer import ModuleColumnsSerializer
from ..sub_views.base import GenericImportView
from drf_yasg import openapi
from rest_framework import status, generics, response
from drf_yasg.utils import swagger_auto_schema


class ModuleColumnsView(generics.RetrieveAPIView, GenericImportView):
    serializer_class = ModuleColumnsSerializer
    response = openapi.Response('response', ModuleColumnsSerializer)

    @swagger_auto_schema(operation_description='Retrieve module columns', responses={status.HTTP_200_OK: response})
    def get(self, request, *args, **kwargs):
        module = load_lib_module(name=kwargs.get('module'))
        serializer = self.get_serializer(data=dict(name=module.name, label=module.label, columns=module.columns))
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.validated_data)
