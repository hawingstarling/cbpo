from django.urls import path

from app.permission.sub_views.access_rule_view import ListCreateAccessRuleView, AccessRuleRetrieveUpdateDestroyView
from app.permission.sub_views.compose_final_permission_view import ComposePermissionView
from app.permission.sub_views.custom_role_view import CustomRoleRetrieveUpdateDetailDeleteOrgClientView, \
    CustomRoleListCreateOrgClientView, CustomRolePreviewOrgClientView
from app.permission.sub_views.permission_group_view import OrgClientPermissionGroupListView

urlpatterns = [
    # Access rules
    path('organizations/<uuid:organization_id>/access-rules/', ListCreateAccessRuleView.as_view(),
         name='org-list-create-access-rule-view'),
    path('organizations/<uuid:organization_id>/access-rules/<pk>/', AccessRuleRetrieveUpdateDestroyView.as_view(),
         name='org-retrieve-update-delete-access-rule-view'),
    path('organizations/<uuid:organization_id>/permission-groups/', OrgClientPermissionGroupListView.as_view(),
         name='org-get-permission-groups-view'),
    # Custom role collection path
    path('organizations/<uuid:organization_id>/custom-roles/', CustomRoleListCreateOrgClientView.as_view(),
         name='org-custom-role-list-create-view'),
    path('organizations/<uuid:organization_id>/custom-roles/<pk>/',
         CustomRoleRetrieveUpdateDetailDeleteOrgClientView.as_view(),
         name='org-custom-role-retrieve-update-destroy-view'),
    path('organizations/<uuid:organization_id>/custom-roles-preview/', CustomRolePreviewOrgClientView.as_view(),
         name='org-custom-role-preview-view'),
    path('organizations/<uuid:organization_id>/users/<uuid:user_id>/custom-roles/',
         ComposePermissionView.as_view(),
         name='compose-permission-org-view')
]
