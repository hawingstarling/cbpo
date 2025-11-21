from django.urls import path
from app.financial.sub_views.organization_view import OrganizationView, OrgClientView, OrgClientSettingView

urlpatterns = [
    path('stats/organizations/', OrganizationView.as_view(), name='list-organizations-view'),
    path('stats/organizations/<uuid:id>/clients/', OrgClientView.as_view(),
         name='list-organization-clients-view'),
    path('stats/organizations-clients/', OrgClientSettingView.as_view(),
         name='list-organization-clients-settings-view')
]
