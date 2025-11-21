from django.urls import path

from app.permission.sub_views.access_rule_view import AccessRuleRetrieveUpdateDestroyView, \
    ListCreateAccessRuleView
from app.permission.sub_views.compose_final_permission_view import ComposePermissionView
from app.permission.sub_views.custom_role_view import CustomRoleRetrieveUpdateDetailDeleteOrgClientView, \
    CustomRoleListCreateOrgClientView, CustomRolePreviewOrgClientView
from app.permission.sub_views.permission_group_view import OrgClientPermissionGroupListView

urlpatterns = [
    path('clients/<uuid:client_id>/access-rules/',
         ListCreateAccessRuleView.as_view(),
         name='list-create-access-rule-client-view'),
    path('clients/<uuid:client_id>/access-rules/<pk>/', AccessRuleRetrieveUpdateDestroyView.as_view(),
         name='client-access-rule-retrieve-update-destroy-view'),
    path('clients/<uuid:client_id>/permission-groups/', OrgClientPermissionGroupListView.as_view(),
         name='client-get-permission-groups-view'),
    # Custom role collection path
    path('clients/<uuid:client_id>/custom-roles/', CustomRoleListCreateOrgClientView.as_view(),
         name='client-custom-role-list-create-view'),
    path('clients/<uuid:client_id>/custom-roles/<pk>/', CustomRoleRetrieveUpdateDetailDeleteOrgClientView.as_view(),
         name='client-custom-role-retrieve-update-destroy-view'),
    path('clients/<uuid:client_id>/custom-roles-preview/', CustomRolePreviewOrgClientView.as_view(),
         name='client-custom-role-preview-view'),
    path('clients/<uuid:client_id>/users/<uuid:user_id>/custom-roles/', ComposePermissionView.as_view(),
         name='compose-permission-client-view')
]
