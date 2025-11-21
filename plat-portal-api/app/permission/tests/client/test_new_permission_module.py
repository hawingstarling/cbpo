from app.permission.models import Permission, OrgClientUserPermission
from app.tenancies.models import UserClient
from app.tenancies.tests.organization.base import OrganizationBaseTest


# Create your tests here.


class NewPermissionModuleTR(OrganizationBaseTest):
    def setUp(self):
        super().setUp()
        self.work_space = self.create_client_organization(
            organization=self.organization, name="TEST-CLIENT-1"
        )
        self.user_client = UserClient.objects.get(user=self.user)

    def test_new_permission_module_TR(self):
        self.client.force_authenticate(user=self.user)
        check_permission_keys = [
            "TR_HISTORY_VIEW",
            "TR_HISTORY_EXTRACT_DATA",
            "TR_SETTING_MANAGEMENT",
            "TR_2D_BARCODE_MANAGEMENT",
            "TR_2D_BARCODE_VIEW",
            "TR_FNSKU_MANAGEMENT",
            "TR_FNSKU_VIEW",
            "TR_SHIPMENT_PLAN_MANAGEMENT_STATUS",
            "TR_SHIPMENT_BOX_DELETE",
            "TR_EFF_REPORT_MANAGEMENT",
            "TR_CUSTOM_SHIPMENT_MANAGEMENT",
            "TR_CUSTOM_SHIPMENT_BOX_DELETE",
            "TR_VENDOR_CENTRAL_MANAGEMENT",
            "TR_SHIPPING_LABEL_MANAGEMENT",
            "TR_SHIPPING_LABEL_HISTORY_MANAGEMENT",
            
        ]
        tr_permissions = Permission.objects.filter(module="TR")
        self.assertEqual(len(check_permission_keys), tr_permissions.count(), "error")

        # CLIENT ADMIN FULL ACCESS
        # user_client_id
        admin_permissions = OrgClientUserPermission.objects.filter(
            object_id=str(self.user_client.id), enabled=True, module="TR"
        )

        check_int = 0
        db_keys = admin_permissions.values_list("key", flat=True)
        for key in db_keys:
            if key in check_permission_keys:
                check_int += 1
        self.assertEqual(len(check_permission_keys), check_int, "error")

    def test_new_permission_module_PF(self):
        check_permission_keys = [
            "SALE_IMPORT",
            "SALE_SINGLE_EDIT",
            "SALE_BULK_EDIT",
            "SALE_VIEW_ALL",
            "SALE_VIEW_24H",
            "SALE_SINGLE_DELETE",
            "SALE_BULK_DELETE",
            "SALE_VIEW_AUDIT_LOG",
            "SALE_REPORT_VIEW_COLUMN",
            "SALE_REPORT_CREATE_COLUMN",
            "SALE_REPORT_EDIT_COLUMN",
            "SALE_REPORT_DELETE_COLUMN",
            "SALE_REPORT_SHARE_COLUMN",
            "SALE_REPORT_VIEW_FILTER",
            "SALE_REPORT_CREATE_FILTER",
            "SALE_REPORT_EDIT_FILTER",
            "SALE_REPORT_DELETE_FILTER",
            "SALE_REPORT_SHARE_FILTER",
            "SALE_REPORT_VIEW_ALL_REPORT",
            "SALE_REPORT_CREATE_REPORT",
            "SALE_REPORT_EDIT_REPORT",
            "SALE_REPORT_DELETE_REPORT",
            "SALE_REPORT_SHARE_REPORT",
            "PF_ITEM_VIEW",
            "PF_ITEM_CREATE",
            "PF_ITEM_EDIT",
            "PF_ITEM_BULK_EDIT",
            "PF_ITEM_DELETE",
            "PF_ITEM_BULK_DELETE",
            "PF_ITEM_IMPORT",
            "ACTIVITY_VIEW",
            "TOOLS_VIEW",
            "SYNC_WORKSPACE",
            "GENERATE_DATASOURCE",
            "CLIENT_SETTINGS_VIEW",
            "CLIENT_SETTINGS_CHANGE",
            "PF_BRAND_SETTING_VIEW",
            "PF_BRAND_SETTING_EDIT",
            "PF_BRAND_SETTING_DELETE",
            "PF_BRAND_SETTING_IMPORT",
            "PF_BRAND_SETTING_EXPORT",
            "PF_BRAND_SETTING_UPDATE_SALES",
            "PF_BRAND_SETTING_UPDATE_ITEMS",
            "PF_OVERVIEW_DASHBOARD_MANAGEMENT",
            "PF_AD_DASHBOARD_MANAGEMENT",
            "PF_FEDEX_VIEW",
            "PF_FEDEX_IMPORT",
            "PF_CUSTOM_REPORT_EXPORT",
            "PF_CUSTOM_REPORT_VIEW",
            "PF_REPRICING_DELETE",
            "PF_REPRICING_EDIT",
            "PF_REPRICING_VIEW",
            "SALE_BULK_PROCESSING_VIEW",
            "PF_TOP_ASINs_VIEW",
            "PF_TOP_ASINs_EDIT",
            "PF_TOP_ASINs_DELETE",
            "PF_TOP_ASINs_IMPORT",
            "PF_TOP_ASINs_EXPORT",
            "PF_EXTENSIV_VIEW",
            "PF_EXTENSIV_EDIT",
            "PF_EXTENSIV_DELETE",
            "PF_EXTENSIV_IMPORT",
            "PF_EXTENSIV_EXPORT",
        ]

        pf_permissions = Permission.objects.filter(module="PF")
        self.assertEqual(len(check_permission_keys), pf_permissions.count(), "error")

        # CLIENT ADMIN FULL ACCESS
        # user_client_id
        admin_permissions = OrgClientUserPermission.objects.filter(
            object_id=str(self.user_client.id), enabled=True, module="PF"
        )

        check_int = 0
        db_keys = admin_permissions.values_list("key", flat=True)
        for key in db_keys:
            if key in check_permission_keys:
                check_int += 1
        self.assertEqual(len(check_permission_keys), check_int, "error")

    def test_new_permission_module_MAP(self):
        self.client.force_authenticate(user=self.user)
        check_permission_keys = [
            "BRAMAN",
            "BRAEXE",
            "MAPMAN",
            "NOTIFI",
            "GSMAPMAN",
            "WALMARTMAN",
            "SIVIEW",
            "SIMAN",
            "DASMAN",
            "ADMINMAN",
            "se_create",
            "se_edit",
            "se_view",
            "se_delete",
            "se_send",
        ]
        mw_permissions = Permission.objects.filter(module="MAP")
        self.assertEqual(len(check_permission_keys), mw_permissions.count(), "error")

        # CLIENT ADMIN FULL ACCESS
        # user_client_id
        admin_permissions = OrgClientUserPermission.objects.filter(
            object_id=str(self.user_client.id), enabled=True, module="MAP"
        )
        check_int = 0
        db_keys = admin_permissions.values_list("key", flat=True)
        for key in db_keys:
            if key in check_permission_keys:
                check_int += 1
        self.assertEqual(
            len(check_permission_keys) - 1, check_int, "error"
        )  # NOTIFI is deny for admin by default -> - 1
