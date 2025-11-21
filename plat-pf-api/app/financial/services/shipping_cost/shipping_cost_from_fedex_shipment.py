import operator
from datetime import timedelta, datetime, timezone
from itertools import groupby
from typing import List
from django.db.utils import DEFAULT_DB_ALIAS
from app.financial.models import LogEntry
from bulk_update.helper import bulk_update
from django.conf import settings
from django.db.models import Sum, Q
from app.core.logger import logger
from app.financial.models import FedExShipment, SaleItem, HighChartMapping, Sale
from app.core.services.audit_logs.base import AuditLogCoreManager
from app.core.services.audit_logs.config import SYSTEM_FEDEX
from app.financial.services.fedex_shipment.config import (
    FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_NONE, FEDEX_SHIPMENT_ONE, FEDEX_SHIPMENT_MULTI, FEDEX_SHIPMENT_COMPLETED)
from app.financial.services.shipping_cost.abstract import ShippingCostService
from app.financial.utils.shipping_cost_helper import separate_shipping_cost_by_accuracy
from app.financial.variable.fulfillment_type import FULFILLMENT_MFN_GROUP, FULFILLMENT_MFN_DS
from app.financial.services.utils.common import round_currency
from app.financial.variable.brand_setting import EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE
from app.financial.variable.sale_status_static_variable import SALE_PENDING_STATUS, SALE_CANCELLED_STATUS
from app.financial.variable.shipping_cost_source import FEDEX_SHIPMENT_SOURCE_KEY, SHIP_CARRIER_FEDEX
from functools import reduce

DATE_RANGE_CONFIG = timedelta(days=settings.DAY_RANGE_FEDEX_SHIPMENT)


class ShippingCostFromFedExShipment(ShippingCostService):

    def __init__(self, sale_item_ids: [str], client_id_only: str, chunk_size: int = 5000, is_recalculate=False, *args,
                 **kwargs):
        super().__init__(sale_item_ids, client_id_only, chunk_size, is_recalculate, *args, **kwargs)
        self._fedex_shipments = []
        self._high_chart_mapping_codes = []
        '''
        ShippingCostFromFedExShipment should consider [FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_NONE] only
        matching jobs are created from specific selected Sale Item Ids
        '''
        self._considerable_fedex_shipment_status = [FEDEX_SHIPMENT_PENDING, FEDEX_SHIPMENT_NONE]
        self._being_update_fedex_shipments_queue = []

    @property
    def _pattern_conditions(self) -> List[Q]:
        return [
            Q(fulfillment_type__name__in=FULFILLMENT_MFN_GROUP, ship_date__isnull=False,
              tracking_fedex_id__isnull=False)
        ]

    def _accuracy_base(self) -> int:
        return EVALUATED_SHIPPING_COST_ACCURACY_ACCEPT_CALCULATE

    @property
    def order_query(self) -> [str]:
        return ['client', 'sale_id', 'ship_date']

    @property
    def select_related(self) -> [str]:
        return ['sale__sale_status', 'fulfillment_type']

    def _bulk_update_external_protected(self):
        bulk_update(self._being_update_fedex_shipments_queue, batch_size=self._size_bulk_update,
                    update_fields=['status', 'matched_sales', 'matched_channel_sale_ids', 'matched_time', 'modified'],
                    using=self.client_db)

    def _exec_sub_mission(self):
        fedex_shipment = FedExShipment.objects.tenant_db_for(self._client_id_only).filter(
            client_id=self._client_id_only, status__in=self._considerable_fedex_shipment_status) \
            .order_by('shipment_date').iterator(chunk_size=self._chunk_size)

        for ele_fedex_shipment in fedex_shipment:
            self._fedex_shipments.append(ele_fedex_shipment)

            if len(self._fedex_shipments) % self._chunk_size == 0:
                self._high_chart_mapping_codes = self._prepare_high_chart_mapping_codes(self._fedex_shipments)
                match_one, match_multi, match_none = self._match_fedex_shipment(self._fedex_shipments)
                sale_stats = self._get_sum_quantity_of_sale_items(match_one)
                self._calculate_shipping_cost(sale_stats, match_one)
                self._update_status_fedex_shipment_not_matched(match_multi, match_none)

        if len(self._fedex_shipments):
            self._high_chart_mapping_codes = self._prepare_high_chart_mapping_codes(self._fedex_shipments)
            match_one, match_multi, match_none = self._match_fedex_shipment(self._fedex_shipments)
            sale_stats = self._get_sum_quantity_of_sale_items(match_one)
            self._calculate_shipping_cost(sale_stats, match_one)
            self._update_status_fedex_shipment_not_matched(match_multi, match_none)

    def _prepare_high_chart_mapping_codes(self, fedex_shipments: [FedExShipment]) -> [dict]:
        """
        prepare high chart mapping codes from Fedex Shipment Set
        :param fedex_shipments:
        :return:
        """
        logger.info(f'[{self.__class__.__name__}][{self._client_id_only}][_prepare_high_chart_mapping_codes')
        recipient_countries = set()
        recipient_states = set()
        for fex_dex_shipment in fedex_shipments:
            recipient_countries.add(fex_dex_shipment.recipient_country)
            recipient_states.add(fex_dex_shipment.recipient_state)

        high_chart_mapping_codes = HighChartMapping.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(
            country_postal_code__in=recipient_countries,
            state_postal_code__in=recipient_states
        ).order_by('country_postal_code', 'state_postal_code').values('state_postal_code', 'state').distinct()

        return list(high_chart_mapping_codes)

    def _prepare_sale_items(self, fedex_shipments: [FedExShipment]) -> [SaleItem]:
        """
        prepare Sale Items from FedEx Shipment Set
        :return:
        """
        logger.info(f'[{self.__class__.__name__}][{self._client_id_only}][_prepare_sale_items]')
        tracking_ids = set()
        for fex_dex_shipment in fedex_shipments:
            tracking_ids.add(fex_dex_shipment.tracking_id)

        if not len(tracking_ids):
            return []

        sale_item_cond = self._base_condition()
        condition_patterns = self._pattern_conditions
        if not self._is_recalculate:
            condition_patterns.extend(self._pattern_conditions_for_not_recalculate)

        for _pattern in condition_patterns:
            sale_item_cond.add(_pattern, Q.AND)

        sale_item_cond.add(Q(client_id=self._client_id_only), Q.AND)

        sale_item_query_set = SaleItem.objects \
            .tenant_db_for(self._client_id_only) \
            .filter(sale_item_cond)
        sale_item_query_set = sale_item_query_set.filter(
            reduce(operator.or_, (Q(tracking_fedex_id__icontains=x) for x in tracking_ids))) \
            .select_related(*self.select_related) \
            .order_by(*self.order_query)

        return list(sale_item_query_set)

    def __parse_group_result_item(self, group_result_item, high_chart_mapping_codes) -> tuple:
        """
        prepare sale item list for matching FedEx
            - compared date from ship date or sale date
            - optional compared state from high chart mapping Model

        :param group_result_item[0] is group key
        :param group_result_item[1] is list of sale items in a group
        :param high_chart_mapping_codes
        :return: (SaleItem)
        """
        group_result_item = (sale_item for _, sale_item in group_result_item)
        try:
            _sale_items_parsed = []
            for _item in group_result_item:
                # insensitive state code
                compared_state_filter = filter(lambda ele: ele.get('state').lower() == _item.sale.state.lower(),
                                               high_chart_mapping_codes)
                try:
                    compared_state = next(compared_state_filter)
                    compared_state = compared_state.get('state_postal_code')
                except StopIteration:
                    compared_state = None
                except AttributeError:
                    compared_state = None
                except Exception as compared_state:
                    logger.error(f'{compared_state}')
                    compared_state = None

                setattr(_item.sale, 'compared_state', compared_state)
                _sale_items_parsed.append(_item)

            return tuple(_sale_items_parsed)
        except Exception as error:
            logger.error(f'[{self.__class__.__name__}]{error}')
            return ()

    def _match_fedex_shipment(self, fedex_shipment: [FedExShipment]):
        logger.info(f'[{self.__class__.__name__}][{self._client_id_only}][_match_fedex_shipment]')
        fedex_shipment_match_one = []
        fedex_shipment_match_multi = []
        fedex_shipment_match_none = []

        group_sale_items = ((sale_item.sale_id, sale_item) for sale_item in self._sub_update_mission)
        group_sale_items = groupby(group_sale_items, lambda ele: ele[0])
        """
        group_result_item[0] is group key as sale_id
        group_result_item[1] is result for each group
        """
        group_sale_items = [(group_result_item[0],
                             self.__parse_group_result_item(group_result_item[1], self._high_chart_mapping_codes)) for
                            group_result_item in group_sale_items]
        for fedex_item in fedex_shipment:
            sales_for_evaluation = []

            # matching with exactly postal code strategy
            for sale_id, _sale_items_in_sale in group_sale_items:
                match_sale = filter(lambda sale_item:
                                    fedex_item.client_id == sale_item.client_id and
                                    str(fedex_item.tracking_id) in str(sale_item.tracking_fedex_id),
                                    _sale_items_in_sale)
                try:
                    res_matched = next(match_sale)  # sale item
                    #
                    sales_for_evaluation.append(res_matched.sale)

                except StopIteration:
                    pass
                except Exception as err_match_sale:
                    logger.error(
                        f'[{self.__class__.__name__}][{self._client_id_only}][match with exactly postal code]err_match_sale {err_match_sale}')
            #
            if len(sales_for_evaluation) == 0:
                fedex_shipment_match_none.append({"fedex_item": fedex_item})
            elif len(sales_for_evaluation) == 1:
                fedex_shipment_match_one.append(
                    {"fedex_item": fedex_item, "sale_id": sales_for_evaluation[0].id,
                     "matched_sales_logs": [ele.id for ele in sales_for_evaluation],
                     "matched_channel_sale_ids": [ele.channel_sale_id for ele in sales_for_evaluation],
                     "matched_time": datetime.now(tz=timezone.utc)})
            elif len(sales_for_evaluation) > 1:
                # evaluate list of matched sales
                is_matched_one_from_evaluation, evaluated_matched_sales = self._evaluate_matching_sales(
                    fedex_item, sales_for_evaluation, fedex_shipment_match_one)
                if is_matched_one_from_evaluation is True:
                    fedex_shipment_match_one.append(
                        {"fedex_item": fedex_item, "sale_id": evaluated_matched_sales[0].id,
                         "matched_sales_logs": [ele.id for ele in evaluated_matched_sales],
                         "matched_channel_sale_ids": [ele.channel_sale_id for ele in evaluated_matched_sales],
                         "matched_time": datetime.now(tz=timezone.utc)})
                else:
                    fedex_shipment_match_multi.append(
                        {"fedex_item": fedex_item,
                         "matched_sales_logs": [ele.id for ele in evaluated_matched_sales],
                         "matched_channel_sale_ids": [ele.channel_sale_id for ele in evaluated_matched_sales],
                         "matched_time": datetime.now(tz=timezone.utc)})

        return fedex_shipment_match_one, fedex_shipment_match_multi, fedex_shipment_match_none

    @classmethod
    def _evaluate_matching_sales(cls, fedex_item: FedExShipment, sales_for_evaluation: [Sale],
                                 fedex_shipment_match_one: []):
        """
        there is only one Sale with valid sale status, left are PENDING or CANCELLED
        """
        # exclude [SALE_PENDING_STATUS, SALE_CANCELLED_STATUS]
        res = list(filter(lambda ele: ele.sale_status.value not in [SALE_PENDING_STATUS, SALE_CANCELLED_STATUS],
                          sales_for_evaluation))
        # filter recipient_name
        if fedex_item.recipient_zip_code:
            res_recipient_zip_code = list(
                filter(lambda ele: ele.postal_code.split('-')[0] == fedex_item.recipient_zip_code.split('-')[0], res))
            if len(res_recipient_zip_code) > 0:
                res = res_recipient_zip_code

        # filter recipient_name
        if fedex_item.recipient_name:
            res_recipient_name = list(
                filter(lambda ele: str(ele.recipient_name).upper() in str(fedex_item.recipient_name).upper(), res))
            if len(res_recipient_name) > 0:
                res = res_recipient_name

        # filter recipient_country
        if fedex_item.recipient_country:
            res_recipient_country = list(
                filter(lambda ele: str(ele.country).upper() == str(fedex_item.recipient_country).upper(), res))
            if len(res_recipient_country) > 0:
                res = res_recipient_country
        # filter recipient_state
        if fedex_item.recipient_state:
            res_recipient_state = list(
                filter(lambda ele: (str(ele.state).upper() == str(fedex_item.recipient_state).upper()) or (
                        fedex_item.recipient_state == ele.compared_state), res))
            if len(res_recipient_state) > 0:
                res = res_recipient_state
        # filter recipient_city
        if fedex_item.recipient_city:
            res_recipient_city = list(
                filter(lambda ele: str(ele.city).upper() == str(fedex_item.recipient_city).upper(), res))
            if len(res_recipient_city) > 0:
                res = res_recipient_city

        # filter with brand name shipper company & brand item or channel brand item match
        if fedex_item.shipper_company:
            res_brand = []
            try:
                for sale in res:
                    items = sale.saleitem_set.tenant_db_for(sale.client_id).all()
                    for item in items:
                        try:
                            if item.fulfillment_type.name == FULFILLMENT_MFN_DS and (
                                    item.brand.name.upper() in fedex_item.shipper_company.upper()
                                    or item.channel_brand.upper() in fedex_item.shipper_company.upper()):
                                res_brand.append(sale)
                                break
                        except Exception as ex:
                            logger.error(f'[{cls.__class__.__name__}][{sale.pk}] {ex}')

                if len(res_brand) > 0:
                    # set res brand when exist sale have brand name or channel brand match with shipper company
                    res = res_brand
            except Exception as ex:
                logger.error(f'[{cls.__class__.__name__}][_evaluate_matching_sales] {ex}')
        #
        res = list(res)
        if len(res) == 1 and res[0].id not in {ele.get('sale_id') for ele in fedex_shipment_match_one}:
            return True, res
        # TODO: evaluate sales closer to fedex shipment_date
        # TODO: I don't think this strategy could be apply for matching Fedex Shipment
        return False, sales_for_evaluation

    def _get_sum_quantity_of_sale_items(self, match_one: []):
        try:
            assert len(match_one) > 0, "match one is not empty"
            sale_id_ids = [item.get('sale_id') for item in match_one]
            return SaleItem.objects.tenant_db_for(self._client_id_only) \
                .filter(sale_id__in=sale_id_ids, ship_carrier__icontains=SHIP_CARRIER_FEDEX) \
                .values('sale_id').annotate(sum_sale_item_quantity=Sum('quantity'))
        except BaseException as err:
            logger.error(f'[{self.__class__.__name__}][__get_sum_quantity_of_sale_items] {err}')
            return []

    def _calculate_shipping_cost(self, sale_stats, sale_match_ones):
        if sale_match_ones:
            sale_id_ids = [item.get('sale_id') for item in sale_match_ones]
            sale_item_query_set_matched = SaleItem.objects.tenant_db_for(self._client_id_only) \
                .filter(sale_id__in=sale_id_ids, ship_carrier__icontains=SHIP_CARRIER_FEDEX)
            for idx, sale_item in enumerate(sale_item_query_set_matched):
                ship_cost, evaluated_accuracy, fedex_matched = self._calc_sale_item_ship_cost(sale_item, sale_stats,
                                                                                              sale_match_ones)
                if ship_cost is None \
                        or (ship_cost == sale_item.shipping_cost
                            and evaluated_accuracy == sale_item.shipping_cost_accuracy
                            and sale_item.shipping_cost_source == FEDEX_SHIPMENT_SOURCE_KEY
                ):
                    if ship_cost is not None:
                        self._add_status_fedex_matched(fedex_matched)
                    continue
                #
                sale_item, changes = separate_shipping_cost_by_accuracy(self._client_id_only, sale_item, ship_cost,
                                                            evaluated_accuracy, FEDEX_SHIPMENT_SOURCE_KEY)
                if changes:
                    sale_item.modified = self._time_now
                    sale_item.dirty = True
                    sale_item.financial_dirty = True
                    #
                    self._being_update_queue.append(sale_item)
                    log_entry = AuditLogCoreManager(client_id=self._client_id_only).set_actor_name(SYSTEM_FEDEX) \
                        .create_log_entry_from_compared_changes(sale_item, changes, action=LogEntry.Action.UPDATE)
                    self._being_update_audit_log_queue.append(log_entry)
                    self._add_status_fedex_matched(fedex_matched)

                if ((idx + 1) % self._size_bulk_update == 0) and len(self._being_update_queue):
                    self._bulk_update()
                    self._being_update_fedex_shipments_queue.clear()

        if len(self._being_update_queue):
            self._bulk_update()
            self._being_update_fedex_shipments_queue.clear()

    def _calc_sale_item_ship_cost(self, sale_item, sale_stats, sale_match_ones):
        """
        :rtype: shipping_cost, evaluated_accuracy
        """
        sale_filter = filter(lambda ele: ele['sale_id'] == sale_item.sale_id, sale_stats)
        fedex_filter = filter(lambda ele: ele['sale_id'] == sale_item.sale_id, sale_match_ones)
        try:
            sale_matched = next(sale_filter)
            sum_sale_item_quantity = sale_matched.get('sum_sale_item_quantity')
        except StopIteration:
            return None, None, None
        try:
            fedex_matched = next(fedex_filter)
            fedex_item = fedex_matched.get('fedex_item')
            # Sum net_charge_amount all item same Tracking ID
            net_charge_amount = FedExShipment.objects.tenant_db_for(self._client_id_only).filter(
                client_id=self._client_id_only, tracking_id=fedex_item.tracking_id).aggregate(
                amount=Sum('net_charge_amount'))
        except StopIteration:
            return None, None, None
        try:
            shipping_cost = (net_charge_amount['amount'] / sum_sale_item_quantity) * sale_item.quantity
            shipping_cost = round_currency(shipping_cost)
            #
            evaluated_accuracy = 100
            return shipping_cost, evaluated_accuracy, fedex_matched
        except BaseException as err:
            logger.error(f'[{self.__class__.__name__}][__calc_sale_item_ship_cost] {err}')
            return None, None, None

    def _add_status_fedex_matched(self, fedex_matched):
        try:
            assert fedex_matched is not None, f"FedEx Matched is not None"
            fedex_item = fedex_matched.get("fedex_item")
            if fedex_item.po_number and fedex_item.customer_ref:
                fedex_item.status = FEDEX_SHIPMENT_COMPLETED
            else:
                fedex_item.status = FEDEX_SHIPMENT_ONE
            fedex_item.matched_time = fedex_matched.get('matched_time')
            fedex_item.matched_sales = list(fedex_matched.get('matched_sales_logs'))
            fedex_item.matched_channel_sale_ids = list(fedex_matched.get('matched_channel_sale_ids'))
            fedex_item.modified = self._time_now
            self._being_update_fedex_shipments_queue.append(fedex_item)
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][_add_status_fedex_matched] {ex}")

    def _update_status_fedex_shipment_not_matched(self, match_multi, match_none):
        bulk_update_box = []
        for item in match_multi:
            fedex_item = item.get("fedex_item")
            fedex_item.matched_sales = list(item.get('matched_sales_logs'))
            fedex_item.matched_channel_sale_ids = list(item.get('matched_channel_sale_ids'))
            fedex_item.matched_time = item.get('matched_time')
            fedex_item.status = FEDEX_SHIPMENT_MULTI
            fedex_item.modified = self._time_now
            bulk_update_box.append(fedex_item)
        for item in match_none:
            fedex_item = item.get("fedex_item")
            fedex_item.status = FEDEX_SHIPMENT_NONE
            fedex_item.modified = self._time_now
            bulk_update_box.append(fedex_item)
        bulk_update(bulk_update_box, batch_size=self._size_bulk_update,
                    update_fields=['status', 'matched_sales', 'matched_channel_sale_ids', 'matched_time', 'modified'],
                    using=self.client_db)


class ShippingCostFromFedExShipment12HRecent(ShippingCostFromFedExShipment):

    @property
    def _pattern_conditions(self) -> List[Q]:
        time_delta_12h = datetime.now(tz=timezone.utc) - timedelta(hours=12)
        return [
            Q(fulfillment_type__name=FULFILLMENT_MFN_GROUP),
            Q(modified__gte=time_delta_12h, ship_date__isnull=False, tracking_fedex_id__isnull=False)
        ]


class ShippingCostFromFedExShipmentPassiveAction(ShippingCostFromFedExShipment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        ShippingCostFromFedExShipmentPassiveAction should consider FEDEX_SHIPMENT_PENDING only
        '''
        self._considerable_fedex_shipment_status = [FEDEX_SHIPMENT_PENDING]

    def _query_fedex_shipment(self):
        return FedExShipment.objects.tenant_db_for(self._client_id_only).filter(
            # limit 10K items to avoid keeping job too long
            status__in=self._considerable_fedex_shipment_status).order_by('shipment_date')[:100000].iterator(
            chunk_size=self._chunk_size)

    def update(self):
        logger.info(f'[{self.__class__.__name__}] automatically calculate ship cost for sale items')
        fedex_shipment_item_query_set = self._query_fedex_shipment()

        for fedex_shipment in fedex_shipment_item_query_set:
            self._fedex_shipments.append(fedex_shipment)

            if len(self._fedex_shipments) % self._chunk_size == 0:
                self._sub_update_mission = self._prepare_sale_items(self._fedex_shipments)
                self._high_chart_mapping_codes = self._prepare_high_chart_mapping_codes(self._fedex_shipments)
                self._exec_sub_mission()

        if len(self._fedex_shipments):
            self._sub_update_mission = self._prepare_sale_items(self._fedex_shipments)
            self._high_chart_mapping_codes = self._prepare_high_chart_mapping_codes(self._fedex_shipments)
            self._exec_sub_mission()

    @property
    def _get_sale_item_query_set(self):
        return []

    def _exec_sub_mission(self):
        match_one, match_multi, match_none = self._match_fedex_shipment(self._fedex_shipments)
        sale_stats = self._get_sum_quantity_of_sale_items(match_one)
        self._calculate_shipping_cost(sale_stats, match_one)
        self._update_status_fedex_shipment_not_matched(match_multi, match_none)

        self._fedex_shipments.clear()
        self._sub_update_mission.clear()
        self._high_chart_mapping_codes.clear()
