import json
import uuid
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from app.core.exceptions import PSServiceException
from app.financial.tests.base import BaseAPITest


class ClientClientUserAPITest(BaseAPITest):

    def test_sync_user_permission1(self):
        self.client_id = uuid.uuid4()
        with self.assertRaises(PSServiceException) as ex:
            with patch('app.core.services.portal_service.PortalService.get_client_setting_user_ps',
                       return_value=self.fake_response_client_setting()):
                url = reverse('client-user-permissions-info',
                              kwargs={
                                  'client_id': self.client_id
                              })
                print("url: {}".format(url))
                headers = {
                    'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.client_id)
                }
                rs = self.client.get(path=url, **headers)
                print(rs)
                self.assertEqual(rs.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_user_permission2(self):
        url = reverse('client-user-permissions-info',
                      kwargs={
                          'client_id': self.client_id
                      })
        print("url: {}".format(url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertTrue(len(content) > 0, msg="content response is not None")

    def test_sync_client1(self):
        url = reverse('create-get-client-sync-portal',
                      kwargs={
                          'client_id': self.client_id
                      })
        print("url: {}".format(url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.post(path=url, **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertTrue(len(content) > 0, msg="content response is not None")

        #
        url = reverse('create-get-client-sync-portal',
                      kwargs={
                          'client_id': self.client_id
                      })
        print("url: {}".format(url))
        headers = {
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(self.jwt_token)
        }
        rs = self.client.get(path=url, **headers)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertTrue(len(content) > 0, msg="content response is not None")
