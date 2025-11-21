from typing import Union

from app.core.logger import logger
from app.financial.models import BrandSetting, SaleItem, SaleItemFinancial
from app.financial.services.utils.common import round_currency
from app.financial.variable.brand_setting import MFN_DROP_SHIP, MFN_RAPID_ACCESS, MFN_STANDARD, \
    PO_DROPSHIP_PERCENT_METHOD, PO_DROPSHIP_COST_METHOD


class ShipCostCalculationAdapter:

    @staticmethod
    def formula_adapter():
        """
        TODO: dynamic formula
        """
        pass

    @staticmethod
    def calc_for_fba(brand_setting: BrandSetting, sale_item: SaleItem):
        try:
            amount = brand_setting.est_fba_fees * sale_item.quantity
            amount = round_currency(amount)
        except Exception as ex:
            # logger.error(f"[calc_for_fba] {ex}")
            amount = None
        return amount

    @staticmethod
    def calc_for_mfn(brand_setting: BrandSetting, sale_item: Union[SaleItem, SaleItemFinancial], sale_stats):
        """
        calculate shipping cost for mfn fulfillment type
        :param brand_setting:
        :param sale_item:
        :param sale_stats:
        :return:
        """
        if brand_setting.mfn_formula in [MFN_DROP_SHIP]:
            return ShipCostCalculationAdapter.calc_for_mfn_for_drop_ship(brand_setting, sale_item)
        if brand_setting.mfn_formula in [MFN_RAPID_ACCESS, MFN_STANDARD]:
            return ShipCostCalculationAdapter.calc_for_mfn_for_rapid_access(brand_setting, sale_item, sale_stats)

        # none or empty MFN formula is ignored
        return None

    @staticmethod
    def calc_for_mfn_for_drop_ship(brand_setting: BrandSetting, sale_item: SaleItem):
        """
        shipping cost for MFN drop ship formula from brand setting
        :param brand_setting:
        :param sale_item:
        :return:
        """
        try:
            amount = brand_setting.est_first_item_shipcost + (
                    (sale_item.quantity - 1) * brand_setting.est_add_item_shipcost)
            amount = round_currency(amount)
        except Exception as ex:
            # logger.error(f"[calc_for_fba] {ex}")
            amount = None
        return amount

    @staticmethod
    def calc_for_mfn_for_rapid_access(brand_setting: BrandSetting, sale_item: SaleItem, sale_stats):
        """
        shipping cost for MFN RA formula from brand setting
        :param brand_setting:
        :param sale_item:
        :param sale_stats:
        :return:
        """
        sale_item_in_stats = filter(
            lambda ele: ele['sale_id'] == sale_item.sale_id and ele['brand_id'] == sale_item.brand_id,
            sale_stats)
        try:
            res = next(sale_item_in_stats)
            sum_sku_quantity = res.get('sum_sku_quantity')
            amount = brand_setting.est_first_item_shipcost + (
                    sale_item.quantity - 1) * brand_setting.est_add_item_shipcost + (
                             brand_setting.po_dropship_cost * sale_item.quantity / sum_sku_quantity)
            amount = round_currency(amount)
            return amount
        except StopIteration:
            return None
        except Exception as err:
            logger.error(f'[{ShipCostCalculationAdapter}] {err}')
            return None

    @staticmethod
    def calc_drop_ship_fee_for_mfn(brand_setting: BrandSetting, sale_item: SaleItem, sale_stats):
        """
        drop ship fee for MFN-DS or MFN-RA ( not MFN-Prime ) from brand setting
        :param brand_setting:
        :param sale_item:
        :param sale_stats:
        :return:
        """
        amount = None
        if brand_setting.po_dropship_method == PO_DROPSHIP_PERCENT_METHOD:
            try:
                assert 0 <= brand_setting.po_dropship_cost <= 100, "po_dropship_cost must have range in [0, 100]"
                amount = (sale_item.cog * brand_setting.po_dropship_cost) / 100
                amount = round_currency(amount)
                return amount
            except Exception as err:
                logger.error(f'[{ShipCostCalculationAdapter}][method={PO_DROPSHIP_PERCENT_METHOD}] {err}')
        else:
            sale_item_in_stats = filter(
                lambda ele: ele['sale_id'] == sale_item.sale_id and ele['brand_id'] == sale_item.brand_id,
                sale_stats)
            try:
                res = next(sale_item_in_stats)
                sum_sku_quantity = res.get('sum_sku_quantity')
                amount = brand_setting.po_dropship_cost / sum_sku_quantity
                amount = round_currency(amount)
                return amount
            except StopIteration:
                pass
            except Exception as err:
                logger.error(f'[{ShipCostCalculationAdapter}][method={PO_DROPSHIP_COST_METHOD}] {err}')
        return amount
