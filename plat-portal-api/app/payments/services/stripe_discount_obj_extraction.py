import operator
from datetime import datetime, timezone
from decimal import Decimal
from functools import reduce
from typing import Union, Any

from app.core.logger import logger
from app.payments.services.utils import StripeApiServices


class StripeDiscountObjExtractionServices:
    """
    extract prop from stripe discount object
    https://stripe.com/docs/api/discounts/object
    """

    def __init__(self, stripe_discount_obj: dict):
        self.stripe_discount_obj = stripe_discount_obj

    def _extract_dict(self, path: str) -> Any:
        try:
            return reduce(operator.getitem, path.split("."), self.stripe_discount_obj)
        except Exception as err:
            logger.error(f"[{self.__class__.__name__}][_extract_dict] invalid path {path}")
            raise err

    def is_valid_discount(self) -> bool:
        val: bool = self._extract_dict(path="coupon.valid")
        return val

    def get_discount_id(self) -> str:
        return self._extract_dict(path="id")

    def get_discount_start(self) -> Union[datetime, None]:
        val: int = self._extract_dict(path="start")
        if val:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        return None

    def get_discount_end(self) -> Union[datetime, None]:
        val: int = self._extract_dict(path="end")
        if val:
            return datetime.fromtimestamp(val, tz=timezone.utc)
        return None

    def get_coupon_promo_code(self) -> str:
        val: str = self._extract_dict(path="promotion_code")
        promotion_code_id = val
        promotion_code_usage = StripeApiServices.get_promo_code_usage(promotion_code_id)
        return promotion_code_usage

    def get_coupon_duration_mode(self) -> str:
        val: str = self._extract_dict(path="coupon.duration")
        return val

    def get_amount_off(self) -> Decimal:
        """
        dollars
        """
        val: float = self._extract_dict(path="coupon.amount_off")
        return Decimal(val / 100) if val is not None else None

    def get_percent_off(self) -> int:
        val: int = self._extract_dict(path="coupon.percent_off")
        return val
