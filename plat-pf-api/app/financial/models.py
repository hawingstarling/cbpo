from django.db.utils import DEFAULT_DB_ALIAS
from app.financial.variable.bulk_sync_datasource_variable import BULK_SYNC_CHUNK_STATUS
import hashlib
import json
import logging
import uuid
from decimal import Decimal
from auditlog.models import LogEntry
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Max, Sum, F, Q, Count
from django.utils import timezone
from django_better_admin_arrayfield.models.fields import ArrayField
from model_utils.models import TimeStampedModel, SoftDeletableModel
from plat_import_lib_api.models import DataImportTemporary
from app.core.services.parser import *
from app.core.variable.permission import MODULE_PF_KEY, MODULE_PF_NAME
from app.financial.variable.activity_variable import ACTION_ACTIVITY
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS_ENUM
from app.financial.variable.sale_status_static_variable import SALE_STATUS_ENUM, RETURN_REVERSED_STATUS, \
    SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS
from app.financial.variable.transaction.generic import USD_CURRENCY, CHANNEL_LISTING_FEE_TYPES, AMAZON_KEY, OE_KEY, \
    TAX_CHARGED_TYPES, FBA_SHIPPING_COST_TYPES, POSTAGE_BILLING_TYPES, RETURN_POSTAGE_BILLING_TYPES, \
    CHANNEL_TAX_WITHHELD, REFUND_ADMIN_FEE_TYPES, OTHER_CHANNEL_FEES_REFUNDED
from app.financial.variable.transaction.type.adjustment import ReversalReimbursementType
from app.financial.variable.transaction.type.charge import PrincipalType
from app.financial.variable.transaction.type.fee import Commission_Type
from app.financial.variable.transaction.type.quantity import QuantityShippedType
from app.database.db.objects_manage import SoftDeleteMultiDbTableManagerBase, MultiDbTableManagerBase
from app.database.db.dynamic_models.cache_transaction import CacheTransactionSoftDeleteMultiTblManager, \
    CacheTransactionMultiTblManager
from app.database.db.dynamic_models.item import ItemSoftDeleteMultiTblManager, ItemMultiTblManager
from app.database.db.dynamic_models.item_cog import ItemCOGSoftDeleteMultiTblManager, ItemCOGMultiTblManager
from app.database.db.dynamic_models.activity import ActivityMultiTblManager
from app.database.db.dynamic_models.log_entry import LogEntryCustomManager
from app.database.db.dynamic_models.sale import SaleSoftDeleteMultiTblManager, SaleMultiTblManager
from app.database.db.dynamic_models.sale_charge_and_cost import SaleChargeSoftDeleteMultiTblManager, \
    SaleChargeMultiTblManager
from app.database.db.dynamic_models.sale_item import SaleItemMultiTblManager, SaleItemSoftDeleteMultiTblManager
from app.database.db.dynamic_models.sale_item_financial import SaleFinancialSoftDeleteMultiTblManager, \
    SaleFinancialMultiTblManager
from app.database.db.dynamic_models.generic_transaction import GenericTransactionSoftDeleteMultiTblManager, \
    GenericTransactionMultiTblManager
from app.database.db.dynamic_models.shipping_invoice import ShippingInvoiceMultiTblManager
from app.database.helper import get_connection_workspace
from .services.fedex_shipment.config import FEDEX_SHIPMENT_CHOICE, FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_SOURCE_IMPORT, \
    FEDEX_SHIPMENT_SOURCE_CHOICE, FEDEX_SHIPMENT_ONE, SHIPPING_INVOICE_PENDING, SHIPPING_INVOICE_DONE_WITH_ERRORS, \
    SHIPPING_INVOICE_DONE, FEDEX_SHIPMENT_COMPLETED
from .variable.alert import REFRESH_RATE_CONFIG, EVERY_15_MINUTE, THROTTLING_PERIOD, EVERY_6_HOUR, \
    ALERT_DELIVERY_VIA_ENUMS, EMAIL_VARIABLE, ALERT_DELIVERY_STATUS_ENUMS
from .variable.brand_setting import PO_DROPSHIP_METHOD_CHOICES, PO_DROPSHIP_COST_METHOD
from .variable.client_setting_variable import SPAPI_RECONNECT_TYPE, SPAPI_RECONNECT_DEFAULT_TYPE
from .variable.common import OPEN_STATUS, BATCH_SIZE_DATA_SEGMENT
from .variable.dashboard import PROPORTION_CHOICE, DEFAULT_PROPORTION
from .variable.data_feed import DATA_FEED_TYPE_CHOICES, FEED_RUN_TYPES_CHOICES, FEED_ACTION_SCHEDULER
from .variable.data_flatten_variable import DATA_FLATTEN_TYPE, FLATTEN_SOURCES, FLATTEN_PG_SOURCE, FLATTEN_SALE_ITEM_KEY
from .variable.job_status import JOB_STATUS, PENDING
from app.core.variable.pf_trust_ac import FINANCIAL_EVENT_TYPE, PF_TRUST_STATUS, PF_TRUST_TYPE
from .variable.report import REPORT_ENUM, REPORTING, REPORT_TYPE_ENUM, ANALYSIS_CR_TYPE
from .variable.sale_item import ENUM_COG_TYPE, COG_TYPE_CALCULATED_KEY
from .variable.segment_variable import HISTORICAL_SYNC_OPTION, SEGMENT_CATEGORY, DIVISION_CATEGORY, SYNC_OPTION_CHOICES
from .variable.transaction.config import TransTypeConfig, TRANS_CATEGORY_CONFIG, FeeCategory, \
    TRANS_EVENT_CONFIG, ShipmentEvent, AdjustmentEvent, RefundEvent, ServiceFeeEvent, ChargeCategory, PromotionCategory, \
    QuantityCategory
from .variable.variant_type_static_variable import VARIANT_TYPE, SHARE_PERMISSION_TYPE, SHARE_MODE_TYPE, \
    SALE_ID_START_NUMBER, PRIVATE_MODE, PUBLIC_MODE
from app.financial.variable.sku_vault import SKU_VAULT_PRIME_TRACK_CONFIG, PRIME_TRACK_SOURCE_CONFIG, SKUVAULT_SOURCE
from app.financial.variable.shipping_cost_source import SHIPPING_COST_SOURCE
from ..database.db.dynamic_models.fedex_shipment import FedExShipmentMultiTblManager
from ..database.db.dynamic_models.sku_vault_prime_track import SKUVaultPrimeTrackSoftDeleteMultiTblManager, \
    SKUVaultPrimeTrackMultiTblManager
from app.extensiv.variables import COGSourceSystem, default_priority_sources

logger = logging.getLogger(__name__)


class FinancialSettings(SoftDeletableModel, TimeStampedModel):
    system_contacts = ArrayField(models.EmailField(unique=True), default=list)
    no_brand_setting_notification_emails = ArrayField(
        models.EmailField(unique=True), default=list)
    no_brand_setting_notification = models.BooleanField(default=True)
    #
    stats_report_notification_emails = ArrayField(models.EmailField(unique=True), default=list,
                                                  verbose_name='Stats list email send report daily')
    stats_report_notification = models.BooleanField(default=True)
    #
    bulk_data_process_limit = models.IntegerField(default=5000,
                                                  verbose_name='Bulk processing data set by limit/threshold of max-capacity of the resource')

    division_max_limit = models.IntegerField(
        default=5, verbose_name='Division max limit')
    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()


class Organization(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    logo = models.CharField(null=True, blank=True, max_length=100)
    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name + " - " + str(self.id)


class ClientPortal(TimeStampedModel, SoftDeletableModel):
    """
    This table fetch from client portal
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True)
    name = models.TextField()
    logo = models.CharField(null=True, blank=True, max_length=100)
    active = models.BooleanField(default=True)
    dashboard_button_color = models.CharField(
        max_length=50, null=True, default="#1985ac")
    account_manager = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    special_project_manager = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    user_sync_info = models.JSONField(default=dict)
    hash_data = models.TextField(default=None, null=True)
    is_oe = models.BooleanField(default=False, verbose_name="IS")

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name + ' - ' + str(self.id)


class ClientSettings(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(ClientPortal, on_delete=models.CASCADE)
    allow_sale_data_update_from = models.DateField(
        null=True, blank=True, default=None)
    time_bulk_processing_notification = models.IntegerField(default=5)
    #
    ac_client_register = models.BooleanField(default=False)
    # MWS
    ac_mws_access_key = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_mws_secret_key = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_mws_merchant_id = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_mws_merchant_name = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_mws_enabled = models.BooleanField(default=False)
    # SPAPI
    ac_spapi_app_id = models.CharField(
        max_length=250, null=True, blank=True, default=None)
    ac_spapi_access_token = models.TextField(
        null=True, blank=True, default=None)
    ac_spapi_refresh_token = models.TextField(
        null=True, blank=True, default=None)
    ac_spapi_token_expired = models.IntegerField(
        null=True, blank=True, default=None)
    ac_spapi_selling_partner_id = models.CharField(
        max_length=250, null=True, blank=True, default=None)
    ac_spapi_auth_code = models.CharField(
        max_length=250, null=True, blank=True, default=None)
    ac_spapi_state = models.CharField(
        max_length=250, null=True, blank=True, default=None)
    ac_spapi_enabled = models.BooleanField(default=False)
    ac_spapi_need_reconnect = models.BooleanField(default=False)
    ac_spapi_type_reconnect = models.CharField(
        max_length=20, choices=SPAPI_RECONNECT_TYPE, default=SPAPI_RECONNECT_DEFAULT_TYPE
    )
    # CartRover
    ac_cart_rover = models.JSONField(default=dict, null=True, blank=True)
    ac_cart_rover_api_user = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_cart_rover_api_key = models.CharField(
        max_length=200, null=True, blank=True, default=None)
    ac_cart_rover_enabled = models.BooleanField(default=False)
    # 3PL Central
    ac_3pl_central_enabled = models.BooleanField(default=False)
    #
    health_hours_check_ac = models.IntegerField(default=1)

    # Widgets
    total_sales_tracker_goal = models.IntegerField(
        default=0, verbose_name="Total Sales Tracker Goal")

    # IT Department
    is_it_department = models.BooleanField(default=False)
    it_department_orders_limit = models.IntegerField(default=20)
    is_remove_cogs_refunded = models.BooleanField(default=False)

    # COGs Config
    # Extensiv
    cog_use_extensiv = models.BooleanField(default=False)
    cog_extensiv_token = models.CharField(
        max_length=255, blank=True, null=True)

    # Data Central
    cog_use_dc = models.BooleanField(default=True)

    # PF COG
    cog_use_pf = models.BooleanField(default=True)

    cog_priority_source = models.JSONField(
        default=default_priority_sources,  # Use a callable for mutable defaults
        blank=True,  # Allow the field to be blank in forms
        # Allow the field to be null in the database (optional, but common for JSONField)
        null=True,
        help_text="Defines the priority order of COGS sources"
    )

    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client}"

    class Meta:
        indexes = [
            models.Index(fields=['client'])
        ]

    @staticmethod
    def validate_cart_rover(client_id: str, data):
        err = {}
        try:
            ins = ClientSettings.objects.tenant_db_for(
                client_id).get(client_id=client_id)
            cart_rover = ins.ac_cart_rover
            merchant_names = [i.get("merchant_name") for i in cart_rover]
            api_users = [i.get("api_user") for i in cart_rover]
            if data["merchant_name"] in merchant_names:
                err.update(
                    {"merchant_name": ["This merchant name already exists"]})
            if data["api_user"] in api_users:
                err.update({"api_user": ["This api user already exists"]})
        except Exception as ex:
            logger.error(f"[{client_id}][validate_cart_rover] {ex}")
            err.update({"system": str(ex)})
        return err


class HighChartMapping(SoftDeletableModel):
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    county = models.CharField(max_length=50, null=True, default=None)
    country_postal_code = models.CharField(max_length=50)
    state_postal_code = models.CharField(max_length=50)
    county_postal_code = models.CharField(
        max_length=50, null=True, default=None)
    state_hc_key = models.CharField(max_length=50)
    county_hc_key = models.CharField(max_length=50, null=True, default=None)
    fips = models.CharField(max_length=50, null=True)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        # unique_together = ['state_hc_key', 'county_hc_key']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['state']),
            models.Index(fields=['county']),
            models.Index(fields=['country_postal_code']),
            models.Index(fields=['state_postal_code']),
            models.Index(fields=['county_postal_code']),
            models.Index(fields=['fips']),
            models.Index(fields=['country', 'state']),
            models.Index(fields=['country', 'state_postal_code']),
            models.Index(fields=['country_postal_code', 'state']),
            models.Index(fields=['country_postal_code', 'state_postal_code']),
        ]


class User(SoftDeletableModel, TimeStampedModel):
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    avatar = models.CharField(max_length=250)
    hash = models.TextField(default=None, null=True)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['user_id', 'hash']),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.email} - {self.username}"


class SaleStatus(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=50, choices=SALE_STATUS_ENUM)
    order = models.IntegerField(default=1000)
    description = models.TextField()

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name + ' - ' + str(self.id)

    class Meta:
        unique_together = ('value', 'order',)
        indexes = [
            models.Index(fields=['value', 'order']),
            models.Index(fields=['value'], name='sale_status_val_idx')
        ]


class ProfitStatus(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=50, unique=True,
                             choices=PROFIT_STATUS_ENUM)
    order = models.IntegerField(default=1000)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name + ' - ' + str(self.id)

    class Meta:
        unique_together = ('value', 'order',)
        indexes = [
            models.Index(fields=['value', 'order']),
            models.Index(fields=['value'], name='profit_status_val_idx')
        ]


class Brand(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    client = models.ForeignKey(
        ClientPortal, on_delete=models.CASCADE, null=True)
    is_obsolete = models.BooleanField(default=False)
    supplier_name = models.CharField(max_length=100, null=True, blank=True)
    acquired_date = models.DateTimeField(null=True, blank=True)
    edi = models.CharField(null=True, blank=True, default=None, max_length=50)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.name} - {self.client}"

    class Meta:
        unique_together = ('name', 'client')
        indexes = [
            models.Index(fields=['name', 'client'])
        ]


class FulfillmentChannel(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=45)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return "{} - {}".format(self.id, self.name)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='fulfillment_type_name_idx')
        ]
        constraints = [
            models.UniqueConstraint(fields=['name'], condition=Q(is_removed=False),
                                    name='fulfillment_channel_not_removed_name_unique_constraint')
        ]


class Variant(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=VARIANT_TYPE)
    name = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=200, blank=True)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name + ' - ' + str(self.id)

    class Meta:
        unique_together = ('type', 'name',)
        indexes = [
            models.Index(fields=['type', 'name'])
        ]


class Channel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True,
                            verbose_name="name of channel")
    label = models.CharField(max_length=100, blank=True, default='')
    use_in_global_filter = models.BooleanField(default=False)
    is_pull_data = models.BooleanField(default=False)
    time_control_priority = models.IntegerField(default=1)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)
        indexes = [
            models.Index(fields=['name'], name='channel_name_idx')
        ]


class StatePopulation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_postal_code = models.CharField(max_length=50)
    state_postal_code = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    est = models.IntegerField()

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ('country_postal_code', 'state_postal_code')


class SaleAbstract(SoftDeletableModel, TimeStampedModel):
    id = models.BigAutoField(primary_key=True, default=3000000, editable=False)
    channel_sale_id = models.CharField(
        max_length=50, blank=True, verbose_name="Channel Sale Id")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    client = models.ForeignKey(
        ClientPortal, on_delete=models.CASCADE, related_name='fk_client_sale')
    sale_status = models.ForeignKey(SaleStatus, on_delete=models.CASCADE, null=True, related_name='fk_sale_status',
                                    verbose_name='Sale Status')
    profit_status = models.ForeignKey(ProfitStatus, on_delete=models.CASCADE, null=True, related_name='fk_sale_profit',
                                      verbose_name='Profit Status')
    date = models.DateTimeField(
        editable=True, blank=True, null=True, verbose_name='Sale Date')
    city = models.CharField(max_length=100, blank=True,
                            null=True, default=None)
    state = models.CharField(max_length=45, blank=True,
                             null=True, default=None, verbose_name='State')
    country = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    postal_code = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    state_key = models.CharField(max_length=50, null=True, default=None)
    county_key = models.CharField(max_length=50, null=True, default=None)
    population = models.ForeignKey(StatePopulation, null=True, default=None, on_delete=models.SET_NULL,
                                   related_name='fk_state_population')
    # address line info
    address_line_1 = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    address_line_2 = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    address_line_3 = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    #
    customer_name = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    recipient_name = models.CharField(
        max_length=100, blank=True, null=True, default=None)

    is_prime = models.BooleanField(
        default=False, null=True, verbose_name='Prime')

    is_replacement_order = models.BooleanField(default=None, null=True)
    replaced_order_id = models.CharField(
        max_length=50, blank=True, verbose_name="Replaced Order Id"
    )

    def __str__(self):
        return f"Channel Sale Id: {self.channel_sale_id} - Channel Id: {self.channel.id} - Client Id: {self.client.id}"

    class Meta:
        abstract = True


class Sale(SaleAbstract):
    objects = SaleSoftDeleteMultiTblManager()
    all_objects = SaleMultiTblManager()

    class Meta:
        unique_together = ('client', 'channel_sale_id', 'channel')
        indexes = [
            models.Index(fields=['client', 'channel_sale_id', 'channel'])
        ]

    @staticmethod
    def generate_id(client_id):
        find = Sale.objects.tenant_db_for(client_id).aggregate(Max('id'))
        id_max = find['id__max']
        if id_max is None:
            return SALE_ID_START_NUMBER
        else:
            return id_max + 1


class SaleChargeAndCostAbstract(SoftDeletableModel, TimeStampedModel):
    id = models.BigAutoField(primary_key=True, editable=False)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)

    def __str__(self):
        return 'Id {} - Sale Id {} - Channel {}'.format(self.id, self.sale.id, self.sale.channel.name)

    class Meta:
        abstract = True

    @property
    def sale_charged(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('sale_charged'))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None

    @property
    def tax_charged(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('tax_charged'))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None

    @property
    def shipping_charged(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('shipping_charged'))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None

    @property
    def total_charged(self):
        try:
            return Decimal(self.sale_charged + self.shipping_charged + self.tax_charged)
        except Exception:
            return None

    @property
    def total_items_cost(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum(F('cog') + F('shipping_cost')))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None

    @property
    def channel_listing_fee(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('channel_listing_fee'))
            agg = agg['total']
            if not agg:
                agg = 0
            return Decimal(agg)
        except Exception:
            return None

    @property
    def other_channel_fees(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('other_channel_fees'))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None

    @property
    def profit(self):
        """
        Charges - Costs - Fees
        :return:
        """
        try:
            return self.total_charged - (self.total_items_cost + self.channel_listing_fee + self.other_channel_fees)
        except Exception:
            return None

    @property
    def margin(self):
        """
        Rate = Profit/Total Charges
        :return:
        """
        if not self.total_charged:
            return None
        try:
            return round(self.profit / self.total_charged, 2)
        except Exception:
            return None

    @property
    def quantity(self):
        try:
            client_id = str(self.sale.client_id)
            agg = SaleItem.objects.tenant_db_for(client_id).filter(sale=self.sale).values('sale').aggregate(
                total=Sum('quantity'))
            agg = agg['total']
            if not agg:
                agg = 0
            return agg
        except Exception:
            return None


class SaleChargeAndCost(SaleChargeAndCostAbstract):
    id = models.BigAutoField(primary_key=True, editable=False)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)

    objects = SaleChargeSoftDeleteMultiTblManager()
    all_objects = SaleChargeMultiTblManager()

    def __str__(self):
        return 'Id {} - Sale Id {} - Channel {}'.format(self.id, self.sale.id, self.sale.channel.name)

    class Meta:
        indexes = [
            models.Index(fields=['sale'], name='sale_charge_and_cost_idx')
        ]


class SaleItemAbstract(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, null=True, blank=True, default=None)
    #
    sale_status = models.ForeignKey(
        SaleStatus, on_delete=models.CASCADE, verbose_name='Sale Status', null=True)
    profit_status = models.ForeignKey(
        ProfitStatus, on_delete=models.CASCADE, null=True, verbose_name='Profit Status')
    fulfillment_type = models.ForeignKey(FulfillmentChannel, on_delete=models.CASCADE, null=True, blank=True,
                                         default=None, verbose_name='Fulfillment Type')
    #
    channel_brand = models.CharField(
        max_length=100, null=True, blank=True, default=None)
    upc = models.CharField(max_length=13, null=True,
                           blank=True, verbose_name='UPC')
    sku = models.CharField(max_length=100, null=False,
                           blank=False, verbose_name='SKU')
    brand_sku = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Brand SKU')
    asin = models.CharField(max_length=10, null=True,
                            blank=True, verbose_name='ASIN')
    quantity = models.IntegerField(default=1, verbose_name='Quantity')
    title = models.CharField(max_length=255, null=True,
                             blank=True, default=None, verbose_name='Title')
    #
    sale_charged = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                       verbose_name='Sale Charged')
    sale_charged_accuracy = models.IntegerField(default=0, null=True)
    #
    shipping_charged = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                           verbose_name='Shipping Charged')
    # COGS
    cog = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True, verbose_name='COG')
    cog_source = models.CharField(
        choices=COGSourceSystem.choices, default=None, null=True, blank=True, max_length=100)
    used_cog_priority = models.IntegerField(
        null=True, default=None, verbose_name='Used COG Source Priority',
        validators=[MinValueValidator(1)]
    )
    unit_cog = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True, verbose_name='Unit COG')
    type_cog = models.CharField(
        choices=ENUM_COG_TYPE, default=COG_TYPE_CALCULATED_KEY, max_length=20)
    #
    estimated_shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                                  verbose_name='Estimated Shipping Cost')
    actual_shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                               verbose_name='Actual Shipping Cost')
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                        verbose_name='Shipping Cost')
    shipping_cost_accuracy = models.IntegerField(default=0, null=True)
    shipping_cost_source = models.CharField(choices=SHIPPING_COST_SOURCE, default=None, null=True, blank=True,
                                            max_length=100)
    #
    warehouse_processing_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True,
                                                   verbose_name='Warehouse Processing Fee')
    warehouse_processing_fee_accuracy = models.IntegerField(default=0, null=True,
                                                            verbose_name='Warehouse Processing Fee Accuracy')
    #
    tax_cost = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True, verbose_name='Tax Cost')
    notes = models.TextField(null=True, blank=True, verbose_name='Notes')
    tax_charged = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                      verbose_name='Tax Charged')
    #
    channel_tax_withheld = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                               verbose_name='Channel Tax Withheld')
    channel_tax_withheld_accuracy = models.IntegerField(null=True)
    #
    ship_date = models.DateTimeField(
        editable=True, blank=True, null=True, verbose_name='Ship Date')
    sale_date = models.DateTimeField(
        editable=True, blank=True, null=True, verbose_name='Sale Date')
    #
    channel_listing_fee = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                              verbose_name='Channel Listing Fee')
    channel_listing_fee_accuracy = models.IntegerField(default=0, null=True)
    #
    other_channel_fees = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                             verbose_name='Other Channel Fees')

    reimbursement_costs = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True,
                                              verbose_name='Reimbursement Costs')

    total_financial_amount = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True)
    #
    dirty = models.BooleanField(default=True)
    resync = models.BooleanField(null=True, default=None)

    refunded_quantity = models.IntegerField(null=True)

    fulfillment_type_accuracy = models.IntegerField(null=True)

    #
    segment = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Segment')
    #
    freight_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                       verbose_name='Freight Cost')
    freight_cost_accuracy = models.IntegerField(null=True)
    #
    inbound_freight_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                               verbose_name='Inbound Freight Cost')
    inbound_freight_cost_accuracy = models.IntegerField(null=True)
    outbound_freight_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                                verbose_name='Outbound Freight Cost')
    outbound_freight_cost_accuracy = models.IntegerField(null=True)
    #
    strategy_id = models.IntegerField(null=True)

    refund_admin_fee = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True)

    tracking_fedex_id = models.CharField(
        max_length=100, blank=True, null=True, default=None)

    user_provided_cost = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                             verbose_name='User Provided Cost')

    ship_carrier = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    # Product & Product Type & Parent ASIN
    product_number = models.CharField(max_length=255, blank=True, null=True, default=None,
                                      verbose_name="Product Number")
    product_type = models.CharField(
        max_length=255, blank=True, null=True, default=None, verbose_name="Product Type")
    parent_asin = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    # Return postage billing
    return_postage_billing = models.DecimalField(max_digits=6, decimal_places=2, default=None, null=True,
                                                 verbose_name='Return Postage Billing')

    # Label Cost
    label_cost = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, null=True)
    label_type = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    class Meta:
        abstract = True


class SaleItem(SaleItemAbstract):
    size = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True, default=None,
                             related_name='fk_sale_item_size')
    style = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True, default=None,
                              related_name='fk_sale_item_style')

    financial_dirty = models.BooleanField(null=True, default=None)

    objects = SaleItemSoftDeleteMultiTblManager()
    all_objects = SaleItemMultiTblManager()

    def __str__(self):
        return 'Id: {} - Sale Id: {} - Client id: {} - SKU: {}'.format(self.id, self.sale.id, self.client.id,
                                                                       self.sku)

    @property
    def total_charged(self):
        try:
            sum_cal = [self.sale_charged,
                       self.shipping_charged, self.tax_charged]
            value = Decimal(sum(filter(None, sum_cal)))
            return value
        except Exception:
            return None

    def __normalize_field_currency(self, field):
        try:
            value = getattr(self, field)
            if value is None:
                value = 0
            return value
        except Exception as ex:
            return 0

    @property
    def total_cost(self):
        try:
            should_use_cog = 0 if self.sale_status.value == SALE_REFUNDED_STATUS else self.cog
            # calculate for values which are not null
            sum_cal = [should_use_cog, self.shipping_cost, self.warehouse_processing_fee, self.channel_listing_fee,
                       self.reimbursement_costs, self.other_channel_fees, self.inbound_freight_cost,
                       self.outbound_freight_cost, self.user_provided_cost, self.refund_admin_fee,
                       self.return_postage_billing]
            value = Decimal(sum(filter(None, sum_cal)))
            return value
        except Exception:
            return None

    @property
    def total_cost_for_profit(self):
        try:
            value = self.total_cost
            exclude = []
            if self.sale_status not in [SALE_REFUNDED_STATUS, SALE_PARTIALLY_REFUNDED_STATUS, RETURN_REVERSED_STATUS]:
                exclude = [self.other_channel_fees,
                           self.reimbursement_costs, self.refund_admin_fee]
            if value is not None:
                value = value - Decimal(sum(filter(None, exclude)))
            return value
        except Exception:
            return None

    @property
    def profit(self):
        """
        Charges - Costs
        :return:
        """
        try:
            return Decimal(
                self.__normalize_field_currency('sale_charged') - self.__normalize_field_currency(
                    'total_cost_for_profit'))
        except Exception:
            return None

    @property
    def margin(self):
        if not self.sale_charged:
            return 0
        try:
            return round((self.profit / self.sale_charged) * 100, 2)
        except Exception:
            return None

    class Meta:
        unique_together = ('client', 'sale', 'sku')
        indexes = [
            models.Index(fields=['client', 'sale', 'sku']),
            models.Index(fields=['client', 'sale']),
            models.Index(fields=['client', 'dirty']),
            models.Index(fields=['client', 'tracking_fedex_id']),
        ]


class SaleItemFinancial(SaleItemAbstract):
    sale_item = models.ForeignKey(
        SaleItem, on_delete=models.CASCADE, null=False)
    #
    size = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True, default=None,
                             related_name='fk_sale_financial_size')
    style = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True, default=None,
                              related_name='fk_sale_financial_style')

    #
    objects = SaleFinancialSoftDeleteMultiTblManager()
    all_objects = SaleFinancialMultiTblManager()

    class Meta:
        unique_together = ('client', 'sale', 'sale_item', 'sku', 'sale_status')
        indexes = [
            models.Index(fields=['client', 'sale',
                                 'sale_item', 'sku', 'sale_status']),
            models.Index(fields=['client', 'sale_item']),
            models.Index(fields=['client', 'dirty']),
            models.Index(fields=['client', 'tracking_fedex_id']),
        ]


class ShareCustom(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField(
        verbose_name='e-mail share custom', null=True)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    permission = models.CharField(
        max_length=50, choices=SHARE_PERMISSION_TYPE, default=SHARE_PERMISSION_TYPE[0][0])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return 'Id {} - User email {} - Client Id {} - Content type : {}'.format(self.id, self.user_email,
                                                                                 self.client.id,
                                                                                 self.content_type)

    class Meta:
        unique_together = ('object_id', 'content_type',
                           'user_email', 'client',)
        ordering = ['-created']


class UserObjectFavorite(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f'Client : {self.client} - Object Id : {self.object_id} - User : {self.user}'

    class Meta:
        ordering = ['-modified']
        unique_together = ['client', 'object_id', 'content_type', 'user']
        indexes = [
            models.Index(
                fields=['client', 'object_id', 'content_type', 'user'])
        ]


class CustomAbstractBase(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    share_mode = models.IntegerField(
        default=PRIVATE_MODE, choices=SHARE_MODE_TYPE)
    share_users = GenericRelation(ShareCustom)
    favorites = GenericRelation(UserObjectFavorite)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f'Name : {self.name} - User: {self.user} - Client: {self.client}'

    class Meta:
        unique_together = ('name', 'client',)
        indexes = [
            models.Index(fields=['client', 'name'])
        ]
        ordering = ['-created']
        abstract = True


class CustomFilter(CustomAbstractBase):
    ds_filter = models.JSONField(default=dict)
    ds_config = models.JSONField(default=dict)


class CustomColumn(CustomAbstractBase):
    ds_column = models.JSONField(default=dict)
    ds_config = models.JSONField(default=dict)


class CustomView(CustomAbstractBase):
    ds_filter = models.JSONField(default=dict)
    ds_column = models.JSONField(default=dict)
    ds_config = models.JSONField(default=dict)
    # tags = PostgresArrayField(models.CharField(unique=True, max_length=50), default=list, blank=True)


class TagClient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100, null=True,
                             blank=True, default=None)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.name}"

    class Meta:
        unique_together = ['client', 'name']
        indexes = [
            models.Index(fields=['client', 'name', 'creator'])
        ]


class TagView(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        ClientPortal, on_delete=models.CASCADE, null=True, blank=True, default=None)
    tag = models.ForeignKey(
        TagClient, on_delete=models.CASCADE, null=True, blank=True, default=None)
    custom_view = models.ForeignKey(CustomView, on_delete=models.CASCADE)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.custom_view} - {self.tag}"

    class Meta:
        unique_together = ['client', 'custom_view', 'tag']
        indexes = [
            models.Index(fields=['client', 'custom_view', 'tag'])
        ]

    @classmethod
    def get_queryset_popular(cls, client_id: str, tag: str = None):
        queryset = cls.objects.tenant_db_for(
            client_id).filter(custom_view__client_id=client_id)
        if tag:
            queryset = queryset.filter(tag__icontains=tag).values('tag') \
                .annotate(total=Count('pk')).order_by('-total')
        else:
            queryset = queryset.order_by('tag')
        return queryset


class TagUserTrack(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    tag = models.ForeignKey(
        TagClient, on_delete=models.CASCADE, null=True, blank=True, default=None)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    is_widget_default = models.BooleanField(default=False)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.tag} - {self.user}"

    class Meta:
        unique_together = ['client', 'tag', 'user']
        indexes = [
            models.Index(fields=['client', 'tag', 'user'])
        ]


class CustomReport(CustomAbstractBase):
    type = models.CharField(max_length=200, choices=REPORT_TYPE_ENUM,
                            default=ANALYSIS_CR_TYPE, null=True, blank=True)
    item_ids = PostgresArrayField(models.UUIDField(
        unique=True), default=list, blank=True)
    ds_query = models.JSONField(default=dict)
    columns = models.JSONField(default=dict)
    bulk_operations = models.JSONField(default=dict)
    status = models.CharField(
        max_length=50, default=REPORTING, choices=REPORT_ENUM)
    progress = models.IntegerField(default=0)
    download_url = models.TextField(default=None, null=True, blank=True)
    share_mode = models.IntegerField(
        default=PUBLIC_MODE, choices=SHARE_MODE_TYPE)
    meta_data = PostgresArrayField(models.CharField(
        unique=True, max_length=100), default=list, blank=True)


class Activity(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=50, choices=ACTION_ACTIVITY)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    #
    objects = ActivityMultiTblManager()
    all_objects = ActivityMultiTblManager()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['client', 'user', 'action']),
            GinIndex(name='json_data_idx', fields=[
                'data'], opclasses=['jsonb_path_ops'])
        ]

    def __str__(self):
        return '{id} - {action} - {client_id}'.format(id=self.id, action=self.action,
                                                      client_id=self.client.pk)


class DataFlattenTrack(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    source = models.CharField(
        max_length=100, choices=FLATTEN_SOURCES, default=FLATTEN_PG_SOURCE)
    type = models.CharField(
        max_length=100, default=DATA_FLATTEN_TYPE[0][0], choices=DATA_FLATTEN_TYPE)
    status = models.CharField(
        max_length=100, default=JOB_STATUS[0][0], choices=JOB_STATUS)
    log = models.TextField(default=None, null=True, blank=True)
    data_source_id = models.CharField(max_length=100, null=True, blank=True,
                                      verbose_name="data source postgres id or external postgres id")
    data_source_es_id = models.CharField(max_length=100, null=True, blank=True,
                                         verbose_name="data source elasticsearch id or external elasticsearch id")
    live_feed = models.BooleanField(default=False)
    last_run = models.DateTimeField(editable=True, blank=True, null=True, default=None,
                                    verbose_name='Last run live feed')
    last_run_event = models.DateTimeField(editable=True, blank=True, null=True, default=None,
                                          verbose_name='Last run trans event')
    log_feed = models.TextField(default=None, null=True, blank=True)
    log_event = models.TextField(default=None, null=True, blank=True)

    # For Tracking Processing Data Source
    batch_size = models.IntegerField(
        default=BATCH_SIZE_DATA_SEGMENT, verbose_name="Per Batch Sync")
    last_rows_synced = models.IntegerField(default=0)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ('client', 'type',)
        ordering = ['-created']

    def __str__(self):
        return '{id} - {client_id} - {type}'.format(id=self.id, client_id=self.client.pk, type=self.type)


class UserPermission(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Info role
    role = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    # Info module
    module = models.CharField(max_length=50, default=MODULE_PF_KEY, null=False)
    module_name = models.CharField(
        max_length=100, default=MODULE_PF_NAME, null=False)
    module_enabled = models.BooleanField(default=False)
    # info permission
    permissions = models.JSONField(default=dict)
    hash_data = models.TextField(default=None, null=True)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ('module', 'client', 'user')
        indexes = [
            models.Index(fields=['client', 'user', 'module', 'module_enabled'])
        ]

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.client, self.user_id, self.role, self.module)


class Item(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, default=None)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    sku = models.CharField(max_length=256, verbose_name='SKU')
    upc = models.CharField(max_length=45, null=True,
                           default=None, blank=True, verbose_name='UPC')
    asin = models.CharField(max_length=45, null=True,
                            default=None, blank=True, verbose_name='ASIN')
    title = models.CharField(max_length=256, null=True,
                             default=None, blank=True, verbose_name='Title')
    description = models.TextField(null=True, blank=True, default=None)
    style = models.ForeignKey(
        Variant, on_delete=models.CASCADE, null=True, related_name='fk_item_style_variant')
    size = models.ForeignKey(Variant, on_delete=models.CASCADE,
                             null=True, related_name='fk_item_size_variant')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    est_shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                            verbose_name='Est. ship cost of one unit')
    est_drop_ship_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                             verbose_name='Est. drop ship cost of one package')
    fulfillment_type = models.ForeignKey(FulfillmentChannel, on_delete=models.CASCADE, null=True, blank=True,
                                         default=None, verbose_name='Fulfillment Type',
                                         related_name='fk_item_fulfillment_type')
    # Product & Product Type & Parent ASIN
    product_number = models.CharField(max_length=255, blank=True, null=True, default=None,
                                      verbose_name="Product Number")
    product_type = models.CharField(
        max_length=255, blank=True, null=True, default=None, verbose_name="Product Type")
    parent_asin = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    #
    objects = ItemSoftDeleteMultiTblManager()
    all_objects = ItemMultiTblManager()

    class Meta:
        unique_together = ('client', 'sku')


class ItemCog(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cog = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                              verbose_name='Cost of Goods')
    effect_start_date = models.DateTimeField(blank=True, null=True, default=None,
                                             verbose_name='Effective Start Date')
    effect_end_date = models.DateTimeField(blank=True, null=True, default=None,
                                           verbose_name='Effective End Date')
    #
    objects = ItemCOGSoftDeleteMultiTblManager()
    all_objects = ItemCOGMultiTblManager()


class GenericTransactionAbstract(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)

    # add column for easy filter data and all field accept null value
    channel_sale_id = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, blank=True, default=None)
    sku = models.CharField(max_length=100, null=True, blank=True, default=None)

    # component amount currency
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    currency = models.CharField(max_length=100, default=USD_CURRENCY)

    # quantity
    quantity = models.IntegerField(null=True)

    # one model for store transaction [SaleItem , ....]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    # sale item date
    date = models.DateTimeField(blank=True, null=True, verbose_name='Date')

    # component type , category transaction
    type = models.CharField(
        max_length=255, choices=TransTypeConfig, default=Commission_Type)
    category = models.CharField(
        max_length=255, choices=TRANS_CATEGORY_CONFIG, default=None, null=True, blank=True)
    event = models.CharField(
        max_length=255, choices=TRANS_EVENT_CONFIG, default=ShipmentEvent)
    seq = models.IntegerField(null=True)
    dirty = models.BooleanField(null=True, default=None)

    class Meta:
        abstract = True


class GenericTransaction(GenericTransactionAbstract):
    #
    objects = GenericTransactionSoftDeleteMultiTblManager()
    all_objects = GenericTransactionMultiTblManager()

    class Meta:
        unique_together = [
            ['client', 'content_type', 'type', 'category', 'event', 'channel_sale_id', 'channel', 'sku', 'seq']]
        indexes = [
            models.Index(fields=['channel_sale_id', 'content_type']),
            models.Index(fields=['client', 'channel',
                                 'content_type', 'dirty', 'date']),
            models.Index(fields=['client', 'channel',
                                 'content_type', 'dirty', 'modified']),
            models.Index(fields=['client', 'channel_sale_id',
                                 'channel', 'sku', 'content_type']),
            models.Index(
                fields=['client', 'channel_sale_id', 'channel', 'sku', 'content_type', 'type', 'category', 'event']),
        ]


class SaleItemTransManager(GenericTransactionMultiTblManager):

    def get_queryset(self):
        content_type = ContentType.objects.db_manager(
            using=self.client_db).get_for_model(SaleItem)
        query_set = super().get_queryset().filter(content_type=content_type)
        return query_set


class SoftDeleteSaleItemTransManager(GenericTransactionSoftDeleteMultiTblManager):

    def get_queryset(self):
        content_type = ContentType.objects.db_manager(
            using=self.client_db).get_for_model(SaleItem)
        query_set = super().get_queryset().filter(content_type=content_type)
        return query_set


class SaleItemTransaction(GenericTransaction):
    objects = SoftDeleteSaleItemTransManager()
    all_objects = SaleItemTransManager()

    class Meta:
        proxy = True

    # define method here

    @property
    def content_object(self):
        try:
            return SaleItem.objects.tenant_db_for(self.client.id).get(channel=self.channel,
                                                                      channel_sale_id=self.channel_sale_id,
                                                                      sku=self.sku)
        except SaleItem.DoesNotExist:
            return None

    @property
    def source(self):
        if self.amount > 0:
            return AMAZON_KEY
        else:
            return OE_KEY

    @property
    def dest(self):
        if self.amount > 0:
            return OE_KEY
        else:
            return AMAZON_KEY

    @staticmethod
    def has_transaction_event(client_id: str, filters_obj: dict):
        cond = Q(**filters_obj)
        count = SaleItemTransaction.objects.tenant_db_for(
            client_id).filter(cond).count()
        if count > 0:
            return True
        return False

    def query_lookup_column(self, column: str, filters_obj: dict, **kwargs):
        args = {
            'channel_listing_fee': self.query_lookup_channel_listing_fee,
            'other_channel_fees': self.query_lookup_other_channel_fees,
            'tax_charged': self.query_lookup_tax_charged,
            'shipping_cost': self.query_lookup_shipping_cost,
            'refunded_quantity': self.query_lookup_refunded_quantity,
            'reimbursement_costs': self.query_lookup_reimbursement_costs,
            'sale_charged': self.query_lookup_sale_charged,
            'channel_tax_withheld': self.query_lookup_channel_tax_withheld,
            'refund_admin_fee': self.query_lookup_refund_admin_fee,
            'return_postage_billing': self.query_return_postage_billing
        }
        column_lookup_trigger = args.get(column, None)
        if not column_lookup_trigger:
            return Q(pk=None)
        return column_lookup_trigger(filters_obj, **kwargs)

    @staticmethod
    def query_lookup_refund_admin_fee(filters_obj: dict, **kwargs) -> Q:
        event = kwargs.get('event')
        if event == RefundEvent or event is None:
            cond = Q(**filters_obj, type__in=REFUND_ADMIN_FEE_TYPES,
                     category=FeeCategory, event=RefundEvent)
        else:
            cond = Q(pk=None)
        return cond

    @staticmethod
    def query_lookup_refunded_quantity(filters_obj: dict, **kwargs) -> Q:
        cond = Q(**filters_obj, type__in=[QuantityShippedType],
                 category=QuantityCategory, event__in=[RefundEvent])
        return cond

    @staticmethod
    def query_lookup_shipping_cost(filters_obj: dict, fulfillment_type: FulfillmentChannel, is_prime: bool = False,
                                   **kwargs) -> Q:
        if fulfillment_type.name == 'FBA':
            cond = Q(**filters_obj, type__in=FBA_SHIPPING_COST_TYPES,
                     category=FeeCategory, event__in=[ShipmentEvent])
        else:
            try:
                del filters_obj['sku']
            except Exception as ex:
                pass
            cond = Q(**filters_obj, type__in=POSTAGE_BILLING_TYPES,
                     event__in=[AdjustmentEvent])
        return cond

    @staticmethod
    def query_lookup_shipping_cost_refunded_postage_billing(filters_obj: dict, **kwargs) -> Q:
        event = kwargs.get('event')
        if event == RefundEvent or event is None:
            try:
                # Adjustment not return SKU from AWS API
                del filters_obj['sku']
            except Exception as ex:
                pass
            sale_filters = Q(**filters_obj)
            # cond : Refund and Reversal Reimbursement from Amazon
            cond = sale_filters & Q(
                event=AdjustmentEvent, type__in=RETURN_POSTAGE_BILLING_TYPES)
        else:
            cond = Q(pk=None)
        return cond

    @staticmethod
    def query_lookup_channel_listing_fee(filters_obj: dict, **kwargs) -> Q:
        cond = Q(**filters_obj, type__in=CHANNEL_LISTING_FEE_TYPES,
                 category=FeeCategory)
        event = kwargs.get('event')
        if event is not None:
            cond = cond & Q(event__in=[event])
        return cond

    @staticmethod
    def query_lookup_other_channel_fees(filters_obj: dict, **kwargs) -> Q:
        sale_item_cond = Q(**filters_obj)
        # cond:
        exclude_type_cond = CHANNEL_LISTING_FEE_TYPES + FBA_SHIPPING_COST_TYPES + TAX_CHARGED_TYPES + \
                            POSTAGE_BILLING_TYPES + RETURN_POSTAGE_BILLING_TYPES + CHANNEL_TAX_WITHHELD + \
                            REFUND_ADMIN_FEE_TYPES + [ReversalReimbursementType]
        category_cond = [FeeCategory, PromotionCategory]
        cond = Q(category__in=category_cond)
        event = kwargs.get('event')
        if event is not None:
            event_types = [event, ServiceFeeEvent]
            if event == ShipmentEvent:
                exclude_type_cond += OTHER_CHANNEL_FEES_REFUNDED
            else:
                cond &= Q(type__in=OTHER_CHANNEL_FEES_REFUNDED)
            cond &= Q(event__in=event_types)
        cond &= ~Q(type__in=exclude_type_cond)
        cond = sale_item_cond & cond
        return cond

    @staticmethod
    def query_lookup_reimbursement_costs(filters_obj: dict, *args, **kwargs):
        event = kwargs.get('event')
        if event == RefundEvent or event is None:
            cond = Q(**filters_obj, event=AdjustmentEvent,
                     type=ReversalReimbursementType)
        else:
            cond = Q(pk=None)
        return cond

    @staticmethod
    def query_lookup_tax_charged(filters_obj: dict, **kwargs) -> Q:
        cond = Q(**filters_obj, type__in=TAX_CHARGED_TYPES,
                 category=ChargeCategory)
        event = kwargs.get('event')
        if event is not None:
            cond = cond & Q(event__in=[event])
        return cond

    @staticmethod
    def query_lookup_channel_tax_withheld(filters_obj: dict, **kwargs) -> Q:
        cond = Q(**filters_obj, type__in=CHANNEL_TAX_WITHHELD,
                 category=ChargeCategory)
        event = kwargs.get('event')
        if event is not None:
            cond = cond & Q(event__in=[event])
        return cond

    def tax_charged(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column('tax_charged', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def channel_listing_fee(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column(
            'channel_listing_fee', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def other_channel_fees(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column(
            'other_channel_fees', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']

        return agg

    def reimbursement_costs(self, client_id: str, filters: dict, **kwargs):
        cond = self.query_lookup_reimbursement_costs(filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def shipping_cost(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column('shipping_cost', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def refunded_quantity(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column('refunded_quantity', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('quantity'))
        agg = agg['total']
        return agg

    def channel_tax_withheld(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column(
            'channel_tax_withheld', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def refund_admin_fee(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column('refund_admin_fee', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg

    def return_postage_billing(self, client_id: str, filters: dict = {}, **kwargs):
        cond = self.query_lookup_column(
            'return_postage_billing', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type') \
            .aggregate(total=Sum('amount'))
        agg = agg['total']
        return agg

    @staticmethod
    def query_return_postage_billing(filters_obj: dict, **kwargs) -> Q:
        event = kwargs.get('event')
        if event == RefundEvent or event is None:
            try:
                # Adjustment not return SKU from AWS API
                del filters_obj['sku']
            except Exception as ex:
                pass
            sale_filters = Q(**filters_obj)
            # cond : Refund and Reversal Reimbursement from Amazon
            cond = sale_filters & Q(
                event=AdjustmentEvent, type__in=RETURN_POSTAGE_BILLING_TYPES)
        else:
            cond = Q(pk=None)
        return cond

    @staticmethod
    def sale_status_of_sale_level(client_id: str, filters: dict = {}, **kwargs):
        # check for 2 case Reimbursed & Return Denied

        sale_client = Q(**filters)

        quantity = kwargs.get('quantity', None)

        query_set = SaleItemTransaction.objects.tenant_db_for(
            client_id).filter(sale_client)

        has_refund = Q(event=RefundEvent)

        reversal_reimbursement = Q(
            event=AdjustmentEvent, type=ReversalReimbursementType)

        quantity_refund = Q(
            event=RefundEvent, category=QuantityCategory, type=QuantityShippedType)

        amount_refund = Q(event=RefundEvent,
                          category=ChargeCategory, type=PrincipalType)

        if query_set.filter(has_refund).count() == 0:
            return None

        # CASE Return Denied:
        if query_set.filter(reversal_reimbursement).count() > 0:
            return RETURN_REVERSED_STATUS

        else:
            refund_quantity = query_set.filter(quantity_refund).values(
                'content_type').aggregate(total=Sum('quantity'))

            refund_quantity = refund_quantity['total']

            is_refund_amount = query_set.filter(amount_refund).count() > 0

            if is_refund_amount:
                if refund_quantity and quantity and refund_quantity < quantity:
                    # CASE Partially Refunded
                    return SALE_PARTIALLY_REFUNDED_STATUS
                else:
                    # CASE REIMBURSED:
                    return SALE_REFUNDED_STATUS

    def get_sale_date_event(self, client_id: str, filters: dict, event: str, **kwargs):
        try:
            cond = Q(**filters) & Q(event=event, date__isnull=False)
            find = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
                value=Max('date'))
            sale_date = find['value']
        except Exception as ex:
            logger.error(f"[get_sale_date_event][{filters}]: {ex}")
            sale_date = None
        return sale_date

    @staticmethod
    def query_lookup_sale_charged(filters_obj: dict, **kwargs) -> Q:
        cond = Q(**filters_obj, type=PrincipalType, category=ChargeCategory)
        event = kwargs.get('event')
        if event is not None:
            cond = cond & Q(event__in=[event])
        return cond

    def sale_charged(self, client_id: str, filters: dict = {}, **kwargs):
        # Calculate sale charged by event
        cond = self.query_lookup_column('sale_charged', filters, **kwargs)
        agg = SaleItemTransaction.objects.tenant_db_for(client_id).filter(cond).values('content_type').aggregate(
            total=Sum('amount'))
        agg = agg['total']
        return agg


class CacheTransactionAbstract(SoftDeletableModel, TimeStampedModel):
    """
    This table using for sync when we need
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel_sale_id = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    # content type of data cache transaction [SaleItem, ...]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    hash = models.TextField(default=None, null=True)
    # text content
    content = models.JSONField(default=dict)

    class Meta:
        abstract = True


class CacheTransaction(CacheTransactionAbstract):
    #
    objects = CacheTransactionSoftDeleteMultiTblManager()
    all_objects = CacheTransactionMultiTblManager()

    #
    class Meta:
        unique_together = ('client', 'channel_sale_id',
                           'channel', 'content_type')
        indexes = [
            models.Index(fields=['client', 'channel_sale_id', 'channel']),
        ]


class CacheSaleItemTransManager(CacheTransactionMultiTblManager):
    def get_queryset(self):
        content_type = ContentType.objects.db_manager(
            using=self.client_db).get_for_model(SaleItem)
        query_set = super().get_queryset().filter(content_type=content_type)
        return query_set


class SoftDeleteCacheSaleItemTransManager(CacheTransactionSoftDeleteMultiTblManager):

    def get_queryset(self):
        content_type = ContentType.objects.db_manager(
            using=self.client_db).get_for_model(SaleItem)
        query_set = super().get_queryset().filter(content_type=content_type)
        return query_set


class CacheSaleItemTransaction(CacheTransaction):
    objects = SoftDeleteCacheSaleItemTransManager()
    all_objects = CacheSaleItemTransManager()

    class Meta:
        proxy = True

    def has_change_content(self, client: ClientPortal, channel_sale_id: str, channel: Channel, content: dict) -> bool:

        # find record cache same data
        try:
            client_id = str(client.pk)
            client_db = get_connection_workspace(client_id)
            hash_data = hashlib.md5(json.dumps(
                content).encode('utf-8')).hexdigest()
            content_type = ContentType.objects.db_manager(
                using=client_db).get_for_model(SaleItem)
            self.objects.tenant_db_for(client_id).get(channel_sale_id=channel_sale_id, channel=channel, client=client,
                                                      content_type=content_type,
                                                      hash=hash_data)
            return False
        except Exception as ex:
            return True


class DataStatus(SoftDeletableModel, TimeStampedModel):
    """
    Model manage PF get data from AC with time period
    concept :
        - job run every day create record trust to AC [client, type & channel] with status Open
        - job every 10 minutes call AC
            + get all records with status Open , Error
            + call API AC service check period [{date} 00:00:00 - {date} 23:59:59] data is ready
                + if is ready -> make status Done -> add job period [{date} 00:00:00 - {date} 23:59:59]
                + if not is ready -> make status Error
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, null=True, blank=True)
    type = models.CharField(
        max_length=100, choices=PF_TRUST_TYPE, default=FINANCIAL_EVENT_TYPE)
    status = models.CharField(
        max_length=100, choices=PF_TRUST_STATUS, default=OPEN_STATUS)
    log = models.TextField(default=None, null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True, default=None)
    # default get orders by modified date from AC
    only_purchased_date = models.BooleanField(default=False)
    # default checking order is prime from 3PL
    is_checking_prime = models.BooleanField(default=False)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ["date"]
        indexes = [
            models.Index(fields=['client', 'channel', 'type']),
            models.Index(fields=['client', 'channel',
                                 'type', 'date', 'priority']),
        ]
        unique_together = ('client', 'channel', 'type', 'date',)


class BrandSetting(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, null=True, default=None, blank=True)
    segment = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='Segment')
    est_first_item_shipcost = models.DecimalField(max_digits=6, decimal_places=2,
                                                  validators=[
                                                      MinValueValidator(0)],
                                                  verbose_name='Est. 1st Item Shipcost')
    est_add_item_shipcost = models.DecimalField(max_digits=6, decimal_places=2,
                                                validators=[
                                                    MinValueValidator(0)],
                                                verbose_name='Est. Add. Item Shipcost')
    est_fba_fees = models.DecimalField(max_digits=6, decimal_places=2,
                                       validators=[MinValueValidator(0)],
                                       verbose_name='Est. FBA Fees')
    est_unit_freight_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                                null=True, blank=True,
                                                validators=[
                                                    MinValueValidator(0)],
                                                verbose_name='Est. Unit Freight Cost')
    est_unit_inbound_freight_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                                        null=True, blank=True,
                                                        verbose_name='Est. Unit Inbound Freight Cost')
    est_unit_outbound_freight_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                                         null=True, blank=True,
                                                         verbose_name='Est. Unit Outbound Freight Cost')
    po_dropship_method = models.CharField(max_length=100, choices=PO_DROPSHIP_METHOD_CHOICES,
                                          default=PO_DROPSHIP_COST_METHOD,
                                          verbose_name='PO Dropship Method')
    po_dropship_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                           validators=[MinValueValidator(0)],
                                           verbose_name='PO Dropship')
    add_user_provided_method = models.CharField(max_length=100, choices=PO_DROPSHIP_METHOD_CHOICES,
                                                default=PO_DROPSHIP_COST_METHOD,
                                                verbose_name='Add. User-Provided Method')
    add_user_provided_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                                 null=True, blank=True,
                                                 validators=[
                                                     MinValueValidator(0)],
                                                 verbose_name='Add. User-Provided')
    mfn_formula = models.CharField(
        max_length=100, null=True, blank=True, verbose_name='MFN Formula')
    auto_update_sales = models.BooleanField(default=False)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ('client', 'channel', 'brand')
        indexes = [
            models.Index(fields=['client', 'channel', 'brand'])
        ]


class BrandMissing(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mapped_brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    client = models.ForeignKey(
        ClientPortal, on_delete=models.CASCADE, null=True)
    is_noticed = models.BooleanField(default=False)

    #
    objects = SoftDeleteMultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        if self.client:
            return f"{self.name}-{self.client.pk}-{self.mapped_brand}"
        else:
            return f"{self.name}-{self.mapped_brand}"

    class Meta:
        unique_together = ('name', 'client', 'mapped_brand')
        indexes = [
            models.Index(fields=['name', 'client'])
        ]


class PostalCodeMapping(models.Model):
    zip_code = models.CharField(max_length=50, null=False)
    fips = models.CharField(max_length=50, null=False)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        indexes = [
            models.Index(fields=['zip_code']),
            models.Index(fields=['fips']),
        ]

    @staticmethod
    def zip_to_fips(zip_code: str):
        """
        Get possible fips values from 5-digits zip code
        @param zip_code: 5-digits zip code
        @return: fips
        """
        if zip_code is None:
            return []
        return PostalCodeMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(zip_code=zip_code[:5]).values_list(
            'fips', flat=True)

    @staticmethod
    def fips_to_zip(fips: str):
        """
        Get possible 5-digits zip code values from fips
        @param fips
        @return: 5-digits zip code
        """
        if fips is None:
            return []
        return PostalCodeMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(fips=fips).values_list('fips',
                                                                                                       flat=True)


class DataFeedTrack(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, default=None)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, null=True, default=None)
    type = models.CharField(
        max_length=100, choices=DATA_FEED_TYPE_CHOICES, default=FLATTEN_SALE_ITEM_KEY)
    action = models.CharField(
        max_length=100, choices=FEED_RUN_TYPES_CHOICES, default=FEED_ACTION_SCHEDULER)
    status = models.CharField(
        max_length=100, choices=JOB_STATUS, default=PENDING)
    latest = models.BooleanField(default=True)
    file_uri = models.URLField()
    date = models.DateField(default=None, null=True, blank=True)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['-created']
        unique_together = ['client', 'channel', 'brand', 'file_uri', 'date']

    def __str__(self):
        return '{client_id} - {channel} - {brand}'.format(channel=self.channel.name, client_id=self.client.pk,
                                                          brand=self.brand.name)


class AutoFeedBrand(TimeStampedModel):
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, null=True, default=None, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ('channel', 'client', 'brand')

    def __str__(self):
        return '{client_id} - {channel} - {brand}'.format(channel=self.channel.name if self.channel else None,
                                                          client_id=self.client.pk,
                                                          brand=self.brand.name)


class ShippingInvoice(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    invoice_number = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    invoice_date = models.DateField(default=None, null=True)
    payer_account_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    payee_account_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    #
    objects = ShippingInvoiceMultiTblManager()
    all_objects = ShippingInvoiceMultiTblManager()

    class Meta:
        unique_together = ['client', 'invoice_number', 'payee_account_id']
        indexes = [
            models.Index(fields=['client', 'invoice_date', 'invoice_number']),
            models.Index(
                fields=['client', 'payer_account_id', 'payee_account_id']),
        ]

    @property
    def agg_trans(self):
        aggr = self.fedexshipment_set \
            .aggregate(
            invoice_balances=Sum('net_charge_amount'),
            total_transactions=Count('pk'),
            matched_transactions=Count('pk', filter=Q(
                status__in=[FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_COMPLETED])),
            matched_sales=Count('matched_sales', filter=Q(
                status__in=[FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_COMPLETED])),
            matched_time=Max('matched_time', filter=Q(
                status__in=[FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_COMPLETED]))
        )
        unmatched_transactions = aggr['total_transactions'] - \
                                 aggr['matched_transactions']
        if aggr['total_transactions'] == aggr['matched_transactions']:
            matching_status = SHIPPING_INVOICE_DONE
        elif unmatched_transactions > 0 and aggr['matched_transactions'] > 0:
            matching_status = SHIPPING_INVOICE_DONE_WITH_ERRORS
        else:
            matching_status = SHIPPING_INVOICE_PENDING
        aggr.update(dict(unmatched_transactions=unmatched_transactions,
                         matching_status=matching_status))
        return aggr

    @property
    def source_files(self):
        try:
            return list(self.fedexshipment_set.tenant_db_for(self.client.id).filter(source_file_url__isnull=False)
                        .values('source_file_name', 'source_file_url').distinct())
        except Exception as ex:
            return []


class FedExShipment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipping_invoice = models.ForeignKey(
        ShippingInvoice, on_delete=models.CASCADE, null=True, default=None)
    transaction_id = models.CharField(
        max_length=256, blank=True, null=True, default=None)
    tracking_id = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    shipper_name = models.CharField(
        max_length=256, blank=True, null=True, default=None)
    shipper_company = models.CharField(
        max_length=256, blank=True, null=True, default=None)
    service_type = models.CharField(
        max_length=100, default=None, null=True, blank=True)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    source = models.CharField(
        max_length=50, choices=FEDEX_SHIPMENT_SOURCE_CHOICE, default=FEDEX_SHIPMENT_SOURCE_IMPORT)
    shipment_date = models.DateField()
    invoice_number = models.CharField(
        max_length=100, blank=True, null=True, default=None)
    invoice_date = models.DateField(default=None, null=True)
    net_charge_amount = models.DecimalField(max_digits=6, decimal_places=2,
                                            validators=[MinValueValidator(0)],
                                            verbose_name='Net Charge Amount')
    recipient_country = models.CharField(
        max_length=15, null=True, default=None, blank=True)
    recipient_state = models.CharField(
        max_length=15, null=True, default=None, blank=True)
    recipient_zip_code = models.CharField(
        max_length=15, null=True, default=None, blank=True)
    recipient_city = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    recipient_name = models.CharField(
        max_length=128, null=True, default=None, blank=True)
    recipient_address_line_1 = models.CharField(
        max_length=256, null=True, default=None, blank=True)
    recipient_address_line_2 = models.CharField(
        max_length=256, null=True, default=None, blank=True)
    # origin
    orig_recipient_country = models.CharField(max_length=15, null=True, default=None, blank=True,
                                              verbose_name='Original Recipient Country/Territory')
    orig_recipient_state = models.CharField(max_length=15, null=True, default=None, blank=True,
                                            verbose_name='Original Recipient State')
    orig_recipient_zip_code = models.CharField(max_length=15, null=True, default=None, blank=True,
                                               verbose_name='Original Recipient Zip Code')
    orig_recipient_city = models.CharField(max_length=100, null=True, default=None, blank=True,
                                           verbose_name='Original Recipient City')
    orig_recipient_name = models.CharField(max_length=128, null=True, default=None, blank=True,
                                           verbose_name='Original Recipient Name')
    orig_recipient_address_line_1 = models.CharField(max_length=256, null=True, default=None, blank=True,
                                                     verbose_name='Original Recipient Address Line 1')
    orig_recipient_address_line_2 = models.CharField(max_length=256, null=True, default=None, blank=True,
                                                     verbose_name='Original Recipient Address Line 2')
    status = models.CharField(
        max_length=50, choices=FEDEX_SHIPMENT_CHOICE, default=FEDEX_SHIPMENT_PENDING)
    matched_sales = PostgresArrayField(
        models.BigIntegerField(unique=True), default=list, blank=True)
    matched_channel_sale_ids = PostgresArrayField(models.CharField(unique=True, max_length=50), default=list,
                                                  blank=True)
    matched_time = models.DateTimeField(null=True)
    source_file_url = models.CharField(
        max_length=500, blank=True, null=True, default=None)
    source_file_name = models.CharField(
        max_length=500, blank=True, null=True, default=None)
    po_number = models.CharField(
        max_length=500, blank=True, null=True, default=None, verbose_name='PO Number')
    customer_ref = models.CharField(max_length=500, blank=True, null=True, default=None,
                                    verbose_name='Customer Reference')

    #
    objects = FedExShipmentMultiTblManager()
    all_objects = FedExShipmentMultiTblManager()

    class Meta:
        verbose_name_plural = 'Shipping Invoice Transactions'
        unique_together = ['client', 'transaction_id', 'shipping_invoice']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['recipient_country',
                                 'recipient_state', 'recipient_zip_code']),
            models.Index(fields=['client', 'tracking_id',
                                 'po_number', 'customer_ref'])
        ]


class AdSpendInformation(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    date = models.DateField()
    sales = models.FloatField()
    spend = models.FloatField()
    impression = models.FloatField()
    acos = models.FloatField(null=True)
    roas = models.FloatField(null=True)
    ad_revenue_1_day = models.FloatField()
    ad_revenue_7_day = models.FloatField()
    ad_revenue_14_day = models.FloatField()
    ad_revenue_30_day = models.FloatField()

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = (('brand', 'date'),)


class SKUVaultPrimeTrack(SoftDeletableModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    channel_sale_id = models.CharField(max_length=50)
    source = models.CharField(
        max_length=50, choices=PRIME_TRACK_SOURCE_CONFIG, default=SKUVAULT_SOURCE)
    status = models.CharField(
        max_length=50, choices=SKU_VAULT_PRIME_TRACK_CONFIG, null=False)

    #
    objects = SKUVaultPrimeTrackSoftDeleteMultiTblManager()
    all_objects = SKUVaultPrimeTrackMultiTblManager()

    class Meta:
        ordering = ['-created']
        unique_together = ['client', 'channel', 'channel_sale_id']
        indexes = [
            models.Index(fields=['client', 'channel', 'channel_sale_id']),
            models.Index(fields=['channel_sale_id'])
        ]

    def __str__(self):
        return f"{self.client} - {self.channel} - {self.channel_sale_id}"


class AppEagleProfile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    profile_id = models.IntegerField()
    profile_name = models.CharField(max_length=500)
    profile_id_link = models.CharField(
        max_length=500, null=True, default=None, blank=True)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['-created']
        unique_together = ['client', 'profile_id']
        indexes = [
            models.Index(fields=['client', 'profile_id'])
        ]

    def __str__(self):
        return f"{self.client} - {self.profile_id}"


class InformedMarketplace(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    informed_co_marketplace_id = models.IntegerField()

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ['client', 'informed_co_marketplace_id']
        indexes = [
            models.Index(fields=['client', 'informed_co_marketplace_id'])
        ]

    def __str__(self):
        return f"{self.client.name} - {self.channel.name} - {self.informed_co_marketplace_id}"


class CustomObject(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.JSONField(null=False)
    hash_content = models.CharField(max_length=32, null=False)  # md5
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['-created']
        unique_together = ['client', 'hash_content']
        indexes = [
            models.Index(fields=['client', 'hash_content'])
        ]


class BulkData(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.JSONField(default=dict, null=True)
    result = models.TextField(default='{}', null=True)
    status = models.CharField(
        max_length=100, choices=BULK_SYNC_CHUNK_STATUS, default=BULK_SYNC_CHUNK_STATUS[0][0])
    data_import = models.ForeignKey(
        DataImportTemporary, on_delete=models.CASCADE)
    client = models.ForeignKey(
        ClientPortal, on_delete=models.CASCADE, null=True)
    hash_data = models.CharField(max_length=32, null=True)  # md5

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'data_import', 'hash_data']
        indexes = [
            models.Index(fields=['client', 'data_import', 'status'])
        ]


class LogClientEntry(LogEntry):
    objects = LogEntryCustomManager()

    class Meta:
        proxy = True


class Alert(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    custom_view = models.ForeignKey(
        CustomView, related_name='alert_info', on_delete=models.CASCADE)
    refresh_rate = models.CharField(
        max_length=50, choices=REFRESH_RATE_CONFIG, default=EVERY_15_MINUTE)
    throttling_alert = models.BooleanField(
        default=False)  # default is disabled
    throttling_period = models.CharField(
        max_length=50, choices=THROTTLING_PERIOD, default=EVERY_6_HOUR)
    users = PostgresArrayField(models.CharField(
        unique=True, max_length=100), default=list, blank=True)  # list username
    phones = PostgresArrayField(models.CharField(
        unique=True, max_length=100), default=list, blank=True)  # list phones
    emails = PostgresArrayField(models.CharField(
        unique=True, max_length=100), default=list, blank=True)  # list emails
    last_refresh_rate = models.DateTimeField(
        null=True, blank=True, default=None)
    last_throttling_period = models.DateTimeField(
        null=True, blank=True, default=None)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'custom_view']
        indexes = [
            models.Index(fields=['client', 'name'])
        ]

    def __str__(self):
        return f"{self.name} - {self.client} - {self.custom_view}"


class AlertDigest(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    is_digest = models.BooleanField(default=False)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'alert', 'name']
        indexes = [
            models.Index(fields=['client', 'alert', 'name'])
        ]

    def __str__(self):
        return f"{self.client} - {self.alert}"


class AlertItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    alert_digest = models.ForeignKey(AlertDigest, on_delete=models.CASCADE)
    sale_item_id = models.UUIDField(default=uuid.uuid4, editable=False)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'alert_digest', 'sale_item_id']
        indexes = [
            models.Index(fields=['client', 'alert_digest', 'sale_item_id'])
        ]

    def __str__(self):
        return f"{self.client} - {self.alert_digest} - {self.sale_item_id}"


class AlertDelivery(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    alert_digest = models.ForeignKey(AlertDigest, on_delete=models.CASCADE)
    via = models.CharField(
        max_length=50, choices=ALERT_DELIVERY_VIA_ENUMS, default=EMAIL_VARIABLE)
    to = PostgresArrayField(models.CharField(
        unique=True, max_length=100), default=list, blank=True)
    status = models.CharField(
        max_length=50, choices=ALERT_DELIVERY_STATUS_ENUMS, default=OPEN_STATUS)
    logs = models.TextField(default=None, null=True)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        ordering = ['created']
        unique_together = ['client', 'alert_digest', 'via']
        indexes = [
            models.Index(fields=['client', 'alert_digest', 'via'])
        ]

    def __str__(self):
        return f"{self.client} - {self.alert_digest} - {self.via} - {self.status}"


class TopProductChannelPerformance(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, null=False, blank=False)
    units_sold = models.IntegerField(default=1)

    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ['client', 'channel', 'sku']
        indexes = [
            models.Index(fields=['client', 'channel', 'sku', 'units_sold'])
        ]

    def __str__(self):
        return f"{self.client} - {self.sku} - {self.units_sold}"


class SaleBySKU(models.Model):
    sku = models.CharField(max_length=100, primary_key=True,
                           null=False, blank=False, verbose_name='SKU')
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        managed = False
        db_table = 'CENSUS_PERSONS'


class ClientUserTrack(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    widget = models.JSONField(default=dict)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.user}"

    class Meta:
        unique_together = ['client', 'user']
        indexes = [
            models.Index(fields=['client', 'user']),
            GinIndex(name='json_widget_idx', fields=[
                'widget'], opclasses=['jsonb_path_ops'])
        ]


class DashboardConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.key} - {self.value}"


class WidgetConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(DashboardConfig, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    icon_url = models.URLField(null=True, blank=True)
    position = models.IntegerField(default=0)
    proportion = models.CharField(
        max_length=255, choices=PROPORTION_CHOICE, default=DEFAULT_PROPORTION)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.dashboard} - {self.key}"

    class Meta:
        unique_together = ['dashboard', 'key']


class ClientDashboardWidget(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    widget = models.ForeignKey(WidgetConfig, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    position_default = models.IntegerField(default=0)
    proportion = models.CharField(
        max_length=255, choices=PROPORTION_CHOICE, default=DEFAULT_PROPORTION)
    settings = models.JSONField(default=dict)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.widget}"

    class Meta:
        unique_together = ['client', 'widget']


class ClientCartRoverSetting(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    merchant_name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    api_user = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    synced = models.BooleanField(default=False)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.merchant_name}"

    class Meta:
        unique_together = ['client', 'api_user', 'api_key']


class DivisionManage(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(
        max_length=255, choices=SEGMENT_CATEGORY, default=DIVISION_CATEGORY)
    key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    settings = models.JSONField(default=dict)
    position = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ["category", "key"]

    def __str__(self):
        return f"{self.category} - {self.key} - {self.name}"


class DivisionClientUserWidget(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=255, choices=SEGMENT_CATEGORY, default=DIVISION_CATEGORY)
    key = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    sync_option = models.CharField(
        max_length=255, choices=SYNC_OPTION_CHOICES, default=HISTORICAL_SYNC_OPTION)
    mtd_target_manual = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                            validators=[MinValueValidator(0)])
    mtd_max_manual = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    ytd_target_manual = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                            validators=[MinValueValidator(0)])
    ytd_max_manual = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    settings = models.JSONField(default=dict)
    position = models.IntegerField(default=0)
    position_default = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)

    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ["client", "category", "key"]

    def __str__(self):
        return f"{self.client} - {self.category} - {self.key}"


class TopClientASINs(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    parent_asin = models.CharField(max_length=255)
    child_asin = models.CharField(max_length=255)
    segment = models.CharField(max_length=100, null=True, blank=True)
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        unique_together = ["client", "channel", "child_asin", "parent_asin"]

    def __str__(self):
        return f"{self.client} - {self.channel} - {self.parent_asin} - {self.child_asin}"
