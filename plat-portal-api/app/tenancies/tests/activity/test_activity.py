import json

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from app.tenancies.config_static_variable import ACTION_ACTIVITY
from app.tenancies.models import Activity, OrganizationUser, UserClient, Client
from app.tenancies.activity_services import ActivityService
from app.tenancies.tests.base import *
from app.tenancies.tests.organization.base import OrganizationBaseTest


class ActivityTest(OrganizationBaseTest):
    EMAIL_FORMAT = 'activity{}@test.com'
    NUMBER_USER_TEST = 10

    def setUp(self):
        init_app_context()
        self.init_list_users(email_format=self.EMAIL_FORMAT, number=self.NUMBER_USER_TEST)
        self.user = User.objects.get(email='activity1@test.com')
        self.client.force_authenticate(user=self.user)
        self.organization = self.create_organization(name="TEST-ORGANIZATION", user=self.user)

    def test_create_activity_with_client_object(self):
        url = reverse(viewname='activities-list-create')
        client = self.create_client_organization(name="Test Client 1", organization=self.organization)
        for action in dict(ACTION_ACTIVITY).keys():
            data = {
                'action': action,
                'data': {
                    'app_profile': 'mwrw'
                },
                'object_id': str(client.pk),
                'object_type': 'client'
            }
            rs = self.client.post(path=url, data=data, format='json')
            print('Create Activity Client Tenancies: {}'.format(rs))
            self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
            content = json.loads(rs.content)
            self.assertNotEqual(content['id'], None, msg='Id not None')
            self.assertEqual(content['object_id'], str(client.pk))
            self.assertEqual(content['object_type'], 'client')
            self.assertEqual(content['user']['user_id'], str(self.user.pk))
            self.assertEqual(content['action'], action)

    def test_create_activity_with_organization_object(self):
        url = reverse(viewname='activities-list-create')
        for action in dict(ACTION_ACTIVITY).keys():
            data = {
                'action': action,
                'data': {
                    'app_profile': 'mwrw'
                },
                'object_id': str(self.organization.pk),
                'object_type': 'organization'
            }
            rs = self.client.post(path=url, data=data, format='json')
            print('Create Activity Organization Tenancies: {}'.format(rs))
            self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
            content = json.loads(rs.content)
            self.assertNotEqual(content['id'], None, msg='Id not None')
            self.assertEqual(content['object_id'], str(self.organization.pk))
            self.assertEqual(content['object_type'], 'organization')
            self.assertEqual(content['user']['user_id'], str(self.user.pk))
            self.assertEqual(content['action'], action)

    def test_verify_query_set(self):
        for action in dict(ACTION_ACTIVITY).keys():
            data = {
                'app_profile': 'mwrw'
            }
            ActivityService.create_activity(user=self.user, data=data, action=action,
                                            object_id=str(self.organization.pk),
                                            object_type=ContentType.objects.get_for_model(self.organization))
        query_set = self.query_set_activity()
        self.assertEqual(query_set.count(), 7)
        #
        query_set = self.query_set_activity(action='SIGN_IN')
        self.assertEqual(query_set.count(), 1)

        #
        query_set = self.query_set_activity(action='ADD_MEMBER')
        self.assertEqual(query_set.count(), 1)

        #
        query_set = self.query_set_activity(action='UPDATE_MEMBER')
        self.assertEqual(query_set.count(), 1)

        #
        query_set = self.query_set_activity(action='DELETE_MEMBER')
        self.assertEqual(query_set.count(), 1)

        #
        query_set = self.query_set_activity(key='sign in')
        self.assertEqual(query_set.count(), 1)

        #
        query_set = self.query_set_activity(action='UERTYUIO')
        self.assertEqual(query_set.count(), 0)
        #
        query_set = self.query_set_activity(key='activity1@test.com')
        self.assertEqual(query_set.count(), 7)
        #
        query_set = self.query_set_activity(action='QWERTYUIO', key='activity1@test.com')
        self.assertEqual(query_set.count(), 0)
        #
        query_set = self.query_set_activity(key='mwrw')
        self.assertEqual(query_set.count(), 7)

    def test_organization_activity(self):
        #
        user1 = User.objects.get(email=self.EMAIL_FORMAT.format(1))
        user2 = User.objects.get(email=self.EMAIL_FORMAT.format(2))
        user3 = User.objects.get(email=self.EMAIL_FORMAT.format(3))
        user4 = User.objects.get(email=self.EMAIL_FORMAT.format(4))
        # create organization
        organization = Organization.objects.create(name='Test Organization1', owner=user1)
        OrganizationUser.objects.create(user=user1, status=MEMBER_STATUS[0][0],
                                        organization=organization, role=RoleService.role_owner())
        # make user to Organizations
        for item in range(2, self.NUMBER_USER_TEST, 1):
            user_invitation = User.objects.get(email=self.EMAIL_FORMAT.format(item))
            self.invitation_organization_accept(organization=organization, user_invitation=user_invitation,
                                                user_create=user1, role_name='staff')
        # TEST ACTIVITY CLIENT
        self.client.force_authenticate(user=user1)
        client = self.create_client_organization(name="Test Client 1", organization=organization)
        # make user to Client
        for item in range(2, self.NUMBER_USER_TEST, 1):
            _user = User.objects.get(email=self.EMAIL_FORMAT.format(item))
            UserClient.objects.create(
                user=_user,
                client=client,
                role=RoleService.role_admin()
            )
        #
        list_users_action = [user1, user2, user3, user4]
        # SIGN_IN
        for _user in list_users_action:
            data = {
                'app_profile': 'mwrw'
            }
            ActivityService.create_activity(user=_user, data=data, action=ActivityService.action_sign_in())

        query = self.query_set_activity()
        self.assertEqual(query.count(), 4)

        # action download map report
        list_users_action = [user1]
        for _user in list_users_action:
            print("Email : {}".format(user1.email))
            data = {
                'app_profile': 'mwrw',
                'module': 'MAP',
                'client_id': str(client.pk),
                'client_name': 'TEST-TEST',
                'report_id': str(client.pk),
                'report_name': 'REPORT-TEST'
            }
            ActivityService.create_activity(user=_user, data=data,
                                            action=ActivityService.action_download_map_report(),
                                            object_id=str(client.pk),
                                            object_type=ContentType.objects.get_for_model(client))
            #
            query = self.query_set_activity(object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 5)
            query = self.query_set_activity(key=_user.email, object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 2)
            query = self.query_set_activity(action=ActivityService.action_download_map_report(),
                                            key=_user.email,
                                            object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 1)
            #
            query = self.query_set_activity(key='REPORT-TEST', object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 1)
            #
            query = self.query_set_activity(key='download map report', object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 1)
            #
            query = self.query_set_activity(key='TEST-TEST', object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 1)
            #
            query = self.query_set_activity(key='mwrw', object=Client, object_ids=[str(client.pk)])
            self.assertEqual(query.count(), 5)

    def query_set_activity(self, action: str = None, key: str = None, object: any = None, object_ids: list = []):
        queryset = Activity.objects.all()
        conditions = ActivityService.get_queryset_filter_action_object(action=action, key=key, object=object,
                                                                       object_ids=object_ids)
        queryset = queryset.filter(conditions) if conditions else queryset
        print('query_set : {}'.format(queryset.query))
        return queryset
