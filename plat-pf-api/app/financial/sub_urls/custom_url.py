from app.financial.sub_views.custom_report_view import CustomReportViewListCreateView, \
    CustomReportRetrieveUpdateDestroyView, CancelCustomReportView
from app.financial.sub_views.custom_object_view import CreateCustomObjectView, RetrieveCustomObjectView
from django.urls import path

from ..sub_views.custom_column_view import CustomColumnListCreateView, CustomColumnRetrieveUpdateDestroyView, \
    CustomColumnListCreateShareModeView
from ..sub_views.custom_filter_view import CustomFilterListCreateView, CustomFilterRetrieveUpdateDestroyView, \
    CustomFilterListCreateShareModeView
from ..sub_views.custom_view import CustomViewListCreateView, CustomViewRetrieveUpdateDestroyView, \
    CustomViewListCreateShareModeView, CustomViewTagFilterView, ClientTagViewSuggestion, ClientTagViewAccess, \
    CustomViewListDropdownView

urlpatterns = [
    # custom filter path
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-filters', CustomFilterListCreateView.as_view(),
         name='client-user-custom-filter-list-create'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-filters/<uuid:pk>',
         CustomFilterRetrieveUpdateDestroyView.as_view(),
         name='client-user-custom-filter-update-retrieve-destroy'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-filters/<uuid:pk>/share-mode',
         CustomFilterListCreateShareModeView.as_view(),
         name='client-user-custom-filter-list-create-share-mode'),
    # Custom column path
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-columns', CustomColumnListCreateView.as_view(),
         name='client-user-custom-column-list-create'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-columns/<uuid:pk>',
         CustomColumnRetrieveUpdateDestroyView.as_view(),
         name='client-user-custom-column-update-retrieve-destroy'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-columns/<uuid:pk>/share-mode',
         CustomColumnListCreateShareModeView.as_view(),
         name='client-user-custom-column-list-create-share-mode'),
    # Custom view path
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-views', CustomViewListCreateView.as_view(),
         name='client-user-custom-view-list-create'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-views/<uuid:pk>',
         CustomViewRetrieveUpdateDestroyView.as_view(),
         name='client-user-custom-view-update-retrieve-destroy'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-views/<uuid:pk>/share-mode',
         CustomViewListCreateShareModeView.as_view(),
         name='client-user-custom-view-list-create-share-mode'),
    #
    path('clients/<uuid:client_id>/custom-views/tags-filters', CustomViewTagFilterView.as_view(),
         name='client-custom-view-tag-filters'),
    path('clients/<uuid:client_id>/custom-views/tags-suggestions', ClientTagViewSuggestion.as_view(),
         name='client-custom-view-tag-suggestion'),
    path('clients/<uuid:client_id>/custom-views/tags-user-access', ClientTagViewAccess.as_view(),
         name='client-custom-view-tag-user-access'),
    path('clients/<uuid:client_id>/custom-views/dropdown', CustomViewListDropdownView.as_view(),
         name='client-custom-view-dropdown'),
    #
    path('clients/<uuid:client_id>/custom-objects', CreateCustomObjectView.as_view(),
         name='client-custom-object-create'),
    path('clients/<uuid:client_id>/custom-objects/<uuid:pk>', RetrieveCustomObjectView.as_view(),
         name='client-custom-object-retrieve'),
    # Custom report
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-reports',
         CustomReportViewListCreateView.as_view(),
         name='client-user-custom-reports-list-create'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-reports/<uuid:pk>',
         CustomReportRetrieveUpdateDestroyView.as_view(),
         name='client-user-custom-reports-update-retrieve-destroy'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-reports/<uuid:pk>/cancellation',
         CancelCustomReportView.as_view(),
         name='cancel-custom-report-progress'),
]
