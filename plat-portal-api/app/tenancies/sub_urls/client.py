from django.urls import path

from ..sub_views.client import (
    ClientRegisterView,
    ClientInformationView,
    ClientModulesView,
    ModuleSwitchingStatusView,
    ClientInvitationView,
    ClientDeleteInvitationView,
    ClientDeleteMemberView,
    ClientMemberAcceptingGETView,
    ClientMemberAcceptingPOSTView,
    UserClientListView,
    UserClientSettingDataView,
    CustomRefreshJSONWebToken,
    UpdateRoleView,
    UsersSuggestionForInvitation,
    ClientModelInternalGetView,
    ForceClientInvitationView, ClientStatusInternalGetView, UserClientTrackLogin,
)

urlpatterns = [
    path("clients/", ClientRegisterView.as_view(), name="client-register"),
    path(
        "clients/<uuid:pk>/", ClientInformationView.as_view(), name="client-information"
    ),
    path(
        "clients/<uuid:client_id>/modules/",
        ClientModulesView.as_view(),
        name="client-modules",
    ),
    path(
        "clients/<uuid:client_id>/modules/<slug:module>/",
        ModuleSwitchingStatusView.as_view(),
        name="client-module-switching",
    ),
    path(
        "clients/<uuid:client_id>/users/invitation/",
        ClientInvitationView.as_view(),
        name="client-inviting-member",
    ),
    path(
        "clients/<uuid:client_id>/users/force-invitation/",
        ForceClientInvitationView.as_view(),
        name="force-client-inviting-member",
    ),
    path(
        "clients/<uuid:client_id>/users/invitation/suggestion/",
        UsersSuggestionForInvitation.as_view(),
        name="list-users-suggestion-for-invitation",
    ),
    path(
        "clients/<uuid:client_id>/users/invitation/<uuid:user_id>/",
        ClientDeleteInvitationView.as_view(),
        name="client-delete-invitation",
    ),
    path(
        "clients/<uuid:client_id>/users/<uuid:user_id>/",
        ClientDeleteMemberView.as_view(),
        name="client-delete-member",
    ),
    path(
        "clients/<uuid:client_id>/users/<uuid:user_id>/roles/",
        UpdateRoleView.as_view(),
        name="client-member-role",
    ),
    path(
        "clients/users/invitation/accept/",
        ClientMemberAcceptingPOSTView.as_view(),
        name="client-member-accepting-post",
    ),
    path(
        "clients/users/invitation/<str:token>/",
        ClientMemberAcceptingGETView.as_view(),
        name="client-member-accepting",
    ),
    path(
        "clients/<uuid:client_id>/users/",
        UserClientListView.as_view(),
        name="client-member-list",
    ),
    # PS-914
    path(
        "clients/<uuid:client_id>/track-active/",
        UserClientTrackLogin.as_view(),
        name="client-user-track-active",
    ),
    path(
        "clients/<uuid:client_id>/users/<uuid:user_id>/settings/",
        UserClientSettingDataView.as_view(),
        name="settings",
    ),
    path(
        "clients/users/jwt-refresh/",
        CustomRefreshJSONWebToken.as_view(),
        name="jwt-refresh",
    ),
    # api public for check client and module is active
    path(
        "clients/<uuid:client_id>/modules/<slug:module>/internal/",
        ClientModelInternalGetView.as_view(),
        name="client-module-public-info",
    ),
    # api internally for check client is active or deleted
    path(
        "in/clients/<uuid:pk>/",
        ClientStatusInternalGetView.as_view(),
        name="client-internal-information",
    ),
]
