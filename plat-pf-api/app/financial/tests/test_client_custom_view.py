from app.financial.tests.base import BaseAPITest


class ClientCustomTypeAPITest(BaseAPITest):

    def test_get_list_custom_view(self):
        print("----- Test API get list custom filter ------")
        self.get_list_custom_type(custom_type="CustomFilter")
        #
        print("----- Test API get list custom column ------")
        self.get_list_custom_type(custom_type="CustomColumn")
        #
        print("----- Test API get list custom view ------")
        self.get_list_custom_type(custom_type="CustomView")

    def test_create_custom_view(self):
        print("----- Test API create custom filter ------")
        content = self.create_custom_type(custom_type="CustomFilter", key_check="ds_filter")
        self.get_list_custom_type(custom_type="CustomFilter", number_records=1)
        self.get_custom_type(custom_type="CustomFilter", obj_id=content['id'])
        #
        print("----- Test API create custom column ------")
        content = self.create_custom_type(custom_type="CustomColumn", key_check="ds_column")
        self.get_list_custom_type(custom_type="CustomColumn", number_records=1)
        self.get_custom_type(custom_type="CustomColumn", obj_id=content['id'])
        #
        print("----- Test API create custom view ------")
        content = self.create_custom_type(custom_type="CustomView", key_check="ds_column")
        self.get_list_custom_type(custom_type="CustomView", number_records=1)
        self.get_custom_type(custom_type="CustomView", obj_id=content['id'])

    def test_update_custom_view(self):
        print("----- Test API create custom filter ------")
        content = self.create_custom_type(custom_type="CustomFilter", key_check="ds_filter")
        data = {
            "name": "CBPO",
            "ds_filter": {
                "alignment": ""
            },
            "ds_config": {},
            "share_mode": 1
        }
        self.update_custom_type(custom_type="CustomFilter", obj_id=content['id'], data=data)
        #
        print("----- Test API create custom column ------")
        content = self.create_custom_type(custom_type="CustomColumn", key_check="ds_column")
        data = {
            "name": "CBPO",
            "ds_column": {
                "field": "A"
            },
            "ds_config": {},
            "share_mode": 1
        }
        self.update_custom_type(custom_type="CustomColumn", obj_id=content['id'], data=data)
        #
        print("----- Test API create custom view ------")
        content = self.create_custom_type(custom_type="CustomView", key_check="ds_column")
        data = {
            "name": "CBPO",
            "ds_column": {
                "field": "A"
            },
            "ds_filter": {
                "alignment": ""
            },
            "ds_config": {},
            "share_mode": 1
        }
        self.update_custom_type(custom_type="CustomView", obj_id=content['id'], data=data)

    def test_delete_custom_view(self):
        print("----- Test API delete custom filter ------")
        content = self.create_custom_type(custom_type="CustomFilter", key_check="ds_filter")
        self.delete_custom_type(custom_type="CustomFilter", obj_id=content['id'])
        #
        print("----- Test API delete custom column ------")
        content = self.create_custom_type(custom_type="CustomColumn", key_check="ds_column")
        self.delete_custom_type(custom_type="CustomColumn", obj_id=content['id'])
        #
        print("----- Test API delete custom view ------")
        content = self.create_custom_type(custom_type="CustomView", key_check="ds_column")
        self.delete_custom_type(custom_type="CustomView", obj_id=content['id'])

    def test_create_share_custom_type(self):
        print("----- Test API share custom filter ------")
        content = self.create_custom_type(custom_type="CustomFilter", key_check="ds_filter")
        data = {
            "share_mode": 1,
            "shared_users": [
                {
                    "user_email": "user_test1@example.com",
                    "permission": "view"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomFilter", obj_id=content['id'], data=data)
        #
        print("----- Test API share custom column ------")
        content = self.create_custom_type(custom_type="CustomColumn", key_check="ds_column")
        data = {
            "share_mode": 0,
            "shared_users": [
                {
                    "user_email": "user_test2@example.com",
                    "permission": "view"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomColumn", obj_id=content['id'], data=data)
        #
        print("----- Test API share custom view ------")
        content = self.create_custom_type(custom_type="CustomView", key_check="ds_column")
        data = {
            "share_mode": 0,
            "shared_users": [
                {
                    "user_email": "user_test3@example.com",
                    "permission": "view"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomView", obj_id=content['id'], data=data)

    def test_get_share_custom_type(self):
        print("----- Test API get share custom filter ------")
        content = self.create_custom_type(custom_type="CustomFilter", key_check="ds_filter")
        data = {
            "share_mode": 1,
            "shared_users": [
                {
                    "user_email": "user_test1@example.com",
                    "permission": "view"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomFilter", obj_id=content['id'], data=data)
        self.get_share_custom_type(obj_id=content['id'], custom_type="CustomFilter", data=data)
        detail = self.get_custom_type(custom_type="CustomFilter", obj_id=content['id'])
        self.assertEqual(detail.get('share_mode'), 1)
        #
        print("----- Test API get share custom column ------")
        content = self.create_custom_type(custom_type="CustomColumn", key_check="ds_column")
        data = {
            "share_mode": 0,
            "shared_users": [
                {
                    "user_email": "user_test2@example.com",
                    "permission": "view"
                },
                {
                    "user_email": "user_test3@example.com",
                    "permission": "edit"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomColumn", obj_id=content['id'], data=data)
        self.get_share_custom_type(obj_id=content['id'], custom_type="CustomColumn", data=data)
        detail = self.get_custom_type(custom_type="CustomColumn", obj_id=content['id'])
        self.assertEqual(detail.get('share_mode'), 0)
        #
        print("----- Test API get share custom view ------")
        content = self.create_custom_type(custom_type="CustomView", key_check="ds_column")
        data = {
            "share_mode": 1,
            "shared_users": [
                {
                    "user_email": "user_test3@example.com",
                    "permission": "edit"
                },
                {
                    "user_email": "user_test4@example.com",
                    "permission": "view"
                }
            ]
        }
        self.create_share_custom_type(custom_type="CustomView", obj_id=content['id'], data=data)
        self.get_share_custom_type(obj_id=content['id'], custom_type="CustomView", data=data)
        detail = self.get_custom_type(custom_type="CustomView", obj_id=content['id'])
        self.assertEqual(detail.get('share_mode'), 1)
