from django.urls import path

from app.tenancies.sub_views.organization import (
    OrganizationRegisterView, OrganizationActionView, OrganizationClientView, OrganizationClientUpdateDeleteView,
    OrganizationUserListView, OrganizationUserUpdateRoleView, OrganizationUserView, OrganizationUserInvitationView,
    OrganizationUserResendInvitationView, OrganizationTokenGETView, OrganizationTokenPOSTView,
    OrganizationAccessClientClientView, UserInfoOrganizationClientClientView, OrganizationRetrieveClientUserView,
    OrganizationApprovalClientToActiveView, OrganizationClientConfigApplication, OrganizationClientConfigSwitcher,
    ForceOrganizationUserInvitationView)

urlpatterns = [

    path('organizations/', OrganizationRegisterView.as_view(),
         name='register-organization'),

    path('organizations/<uuid:pk>/',
         OrganizationActionView.as_view(),
         name='retrieve-update-destroy-organization'),

    path('organizations/<uuid:pk>/clients/',
         OrganizationClientView.as_view(),
         name='list-create-organization-client'),

    path('organizations/<uuid:pk>/clients/<uuid:client_id>/',
         OrganizationClientUpdateDeleteView.as_view(),
         name='update-delete-organization-client'),

    path('organizations/<uuid:pk>/users/',
         OrganizationUserListView.as_view(),
         name='user-manage-organization'),

    path('organizations/<uuid:pk>/users/<uuid:user_id>/',
         OrganizationUserView.as_view(),
         name='retrieve-delete-user-manage-organization'),

    path('organizations/<uuid:pk>/users/<uuid:user_id>/client/',
         OrganizationRetrieveClientUserView.as_view(),
         name='organization-list-client-grant-to-user'),

    path('organizations/<uuid:pk>/users/<uuid:user_id>/role/',
         OrganizationUserUpdateRoleView.as_view(),
         name='role-user-manage-organization'),

    path('organizations/<uuid:pk>/users/<uuid:user_id>/clients/grant_access/',
         OrganizationAccessClientClientView.as_view(),
         name='organization-user-access-to-clients'),

    path('organizations/<uuid:pk>/users/invitation/',
         OrganizationUserInvitationView.as_view(),
         name='organization-invitation-users'),

    path('organizations/<uuid:pk>/users/force-invitation/',
         ForceOrganizationUserInvitationView.as_view(),
         name='force-organization-invitation-users'),

    path('organizations/<uuid:pk>/users/<uuid:user_id>/resend-invitation/',
         OrganizationUserResendInvitationView.as_view(),
         name='organization-resend-invitation-users'),

    path('organizations/users/invitation/accept/',
         OrganizationTokenPOSTView.as_view(),
         name='organization-invitation-users-validate-token-post'),

    path('organizations/users/invitation/<str:token>/',
         OrganizationTokenGETView.as_view(),
         name='organization-invitation-users-validate-token'),

    path('me/organizations/and/clients/',
         UserInfoOrganizationClientClientView.as_view(),
         name='get-info-organization-and-clients-user'),

    path('organizations/<uuid:pk>/clients/<uuid:client_id>/approve/',
         OrganizationApprovalClientToActiveView.as_view(),
         name='organization-approval-client-to-active'),
    path('organizations/<uuid:pk>/clients/<uuid:client_id>/apps/',
         OrganizationClientConfigApplication.as_view(),
         name='organization-client-application-list'),
    path('organizations/<uuid:pk>/clients/<uuid:client_id>/apps/<slug:app>/',
         OrganizationClientConfigSwitcher.as_view(),
         name='organization-client-switching-application')
]
