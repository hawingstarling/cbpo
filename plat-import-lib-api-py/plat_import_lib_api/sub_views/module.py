from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plat_import_lib_api.services.utils.utils import get_modules_config_template
from plat_import_lib_api.sub_views.base import GenericImportView


class ImportModuleListView(generics.ListAPIView, GenericImportView):

    def get_queryset(self):
        module = self.kwargs.get('module')
        return self.queryset.filter(module=module).order_by('-created')


class ListModuleKeysView(APIView):
    permission_classes = [AllowAny]

    @property
    def modules_filters(self):
        return ['all']

    def get(self, request, *args, **kwargs):
        modules_config = get_modules_config_template(self.modules_filters)
        return Response(modules_config, status=status.HTTP_200_OK)
