from django.conf.urls import url
from django.urls import include, path
from plat_import_lib_api.sub_views.process import ProcessDataImportView

from app.financial.sub_views.import_view import ListClientModuleKeysView, ClientListImportHistoryView

urlpatterns = [
    url(r'^imports/', include('plat_import_lib_api.urls')),
    path('clients/<uuid:client_id>/imports/history',
         ClientListImportHistoryView.as_view(), name='client-import-history'),
    path('clients/<uuid:client_id>/imports/modules-keys',
         ListClientModuleKeysView.as_view(), name='client-import-modules-keys'),
    path('clients/<uuid:client_id>/imports/<slug:module>/<uuid:import_id>/process',
         ProcessDataImportView.as_view(), name='client-process-import-module'),
]
