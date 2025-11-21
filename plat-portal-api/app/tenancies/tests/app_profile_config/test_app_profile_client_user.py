import json

from django.urls import reverse
from rest_framework import status

from app.tenancies.config_app_and_module import APP_NAME_BUILD_PROFILE, APP_BUILD_PROFILE_CONFIG
from app.tenancies.services import AppClientConfigService, UserClientService
from app.tenancies.tests.organization.base import OrganizationBaseTest


class AppProfileConfig(OrganizationBaseTest):
    password = "1234567890"
    app_profile = APP_NAME_BUILD_PROFILE

    def setUp(self) -> None:
        self.user = self.init_user(email="owner@test.com", password=self.password)
        self.organization = self.create_organization(name="TBD", user=self.user)
        self.ws = self.create_client_organization(name="WS TBD", organization=self.organization)
        self.init_list_users()

    def test_get_app_profile_client_user(self):
        # List app client user
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="organization-client-application-list",
                      kwargs={"pk": str(self.organization.pk), "client_id": str(self.ws.pk)})
        rs = self.client.get(path=url, data=None, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        for item in content:
            self.assertEqual(item['app'] in APP_BUILD_PROFILE_CONFIG, True)
            self.assertNotEqual(item['label'], None, msg="label is not None")
            self.assertNotEqual(item['enabled'], None, msg="enabled is not None")

    def verify_get_app_profile_client_user(self, app: str = None, enabled: bool = False):
        # List app client user
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="organization-client-application-list",
                      kwargs={"pk": str(self.organization.pk), "client_id": str(self.ws.pk)})
        rs = self.client.get(path=url, data=None, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        for item in content:
            self.assertEqual(item['app'] in APP_BUILD_PROFILE_CONFIG, True)
            self.assertNotEqual(item['label'], None, msg="label is not None")
            self.assertNotEqual(item['enabled'], None, msg="enabled is not None")
            if app == item['app']:
                self.assertEqual(item['enabled'], enabled)

    def test_update_app_profile_client_user(self):
        # Update mwrw
        self.verify_get_app_profile_client_user(app="mwrw", enabled=False)
        self.client.force_authenticate(user=self.user)
        url = reverse(viewname="organization-client-switching-application",
                      kwargs={"pk": str(self.organization.pk), "client_id": str(self.ws.pk),
                              "app": "mwrw"})
        data = {"enabled": True}
        rs = self.client.post(path=url, data=data, format='json')
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        self.verify_get_app_profile_client_user(app="mwrw", enabled=True)

    def test_get_client_by_app_profile(self):
        self.client.force_authenticate(user=self.user)
        # default app = mwrw
        client = self.create_client_organization(name="WS TBD 1", organization=self.organization)
        # Enable client for app
        query_set = UserClientService.get_query_set_access_of_user(organization=self.organization,
                                                                   user=self.user,
                                                                   active=True)
        # Join check config app client
        query_set_client_access = AppClientConfigService.get_client_query_set_join_client_app_profile(query_set)
        self.assertEqual(query_set_client_access.count(), 2)

        # enable client for app remain
        app_another = set(APP_NAME_BUILD_PROFILE) - {'mwrw'}
        for app in app_another:
            print("app name : {}".format(app))
            AppClientConfigService.create_client_app_profile(client=client, app=app, enabled=True)
            query_set_client_access = AppClientConfigService.get_client_query_set_join_client_app_profile(query_set,
                                                                                                          app_profile=app)
            self.assertEqual(query_set_client_access.count(), 1)
