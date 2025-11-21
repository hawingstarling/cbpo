from plat_import_lib_api.sub_views.module import ListModuleKeysView
from plat_import_lib_api.sub_views.base import ListImportHistoryView


class ListClientModuleKeysView(ListModuleKeysView):
    @property
    def modules_filters(self):
        return ['FedExShipmentModule', 'SaleItem']


class ClientListImportHistoryView(ListImportHistoryView):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(module__in=['FedExShipmentModule', 'SaleItem'])
