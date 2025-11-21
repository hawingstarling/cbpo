from app.core.variable.marketplace import CHANNEL_DEFAULT
from app.financial.models import SaleItem, FulfillmentChannel, BrandSetting
from app.financial.services.sale_item_mapping.builder import MappingSaleItemBuilder
from app.financial.tests.base import BaseAPITest
from app.financial.variable.brand_setting import MFN_DROP_SHIP, MFN_RAPID_ACCESS
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN, FULFILLMENT_MFN_DS, FULFILLMENT_MFN_RA
from config.settings.common import ROOT_DIR

APPS_DIR = ROOT_DIR.path('app')

fixtures = [
    APPS_DIR + "financial/tests/fixtures/organization.json",
    APPS_DIR + "financial/tests/fixtures/clientportal.json",
    APPS_DIR + "financial/tests/fixtures/client_settings.json",
    APPS_DIR + "financial/tests/fixtures/brand.json",
    APPS_DIR + "financial/tests/fixtures/fulfillmentchannel.json",
    APPS_DIR + "financial/tests/fixtures/channel.json",
    APPS_DIR + "financial/tests/fixtures/sale_status.json",
    APPS_DIR + "financial/tests/fixtures/profit_status.json",
    APPS_DIR + "financial/tests/fixtures/sale.json",
    APPS_DIR + "financial/tests/fixtures/sale_charge_and_cost.json",
    APPS_DIR + "financial/tests/fixtures/sale_item.json",
    APPS_DIR + "job/tests/fixtures/job_config.json",
]


class MappingSaleItemMFNClassificationTestCase(BaseAPITest):
    fixtures = fixtures

    def setUp(self):
        super().setUp()

        self.marketplace = CHANNEL_DEFAULT

        # create table manage data sale items
        self.create_flatten_manage_sale_items()

        self.client_id = '1dd0bded-e981-4d2f-9bef-2874016661e7'
        #
        self.first_record = SaleItem.objects.tenant_db_for(self.client_id).order_by('created').first()

        self.sale_item_ids = [str(self.first_record.pk)]

        self.ff_mfn = FulfillmentChannel.objects.tenant_db_for(self.client_id).get(name=FULFILLMENT_MFN)

        self.channel_us_id = "4c3c7cdc-4297-4ff5-aa35-aa388c1f4e14"
        self.brand_id = "02edd561-1084-4f55-bd5c-9222d008df4e"

        self.brand_setting = BrandSetting.objects.tenant_db_for(self.client_id).create(client_id=self.client_id,
                                                                                       channel_id=self.channel_us_id,
                                                                                       brand_id=self.brand_id,
                                                                                       est_first_item_shipcost=1,
                                                                                       est_add_item_shipcost=1,
                                                                                       est_fba_fees=1,
                                                                                       est_unit_inbound_freight_cost=1,
                                                                                       est_unit_outbound_freight_cost=1,
                                                                                       po_dropship_cost=1,
                                                                                       mfn_formula=MFN_DROP_SHIP)

    def test_mfn_classification(self):
        self.first_record.fulfillment_type = self.ff_mfn
        self.first_record.fulfillment_type_accuracy = None
        self.first_record.save()

        builder_dc = MappingSaleItemBuilder.instance() \
            .tenant_db_for_only(self.client_id) \
            .tenant_db_for_only(self.client_id) \
            .with_selected_sale_item_ids(self.sale_item_ids)
        handler_dc = builder_dc.build_mapping_mfn_classification()
        handler_dc.exec()

        self.first_record.refresh_from_db()

        self.assertEqual(self.first_record.fulfillment_type.name, FULFILLMENT_MFN_DS)

        # is override
        self.brand_setting.mfn_formula = MFN_RAPID_ACCESS
        self.brand_setting.save()

        handler_dc = builder_dc.with_override_mode(True).build_mapping_mfn_classification()
        handler_dc.exec()

        self.first_record.refresh_from_db()

        self.assertEqual(self.first_record.fulfillment_type.name, FULFILLMENT_MFN_RA)
