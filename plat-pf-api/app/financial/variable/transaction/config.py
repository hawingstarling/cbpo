from app.financial.variable.transaction.type.adjustment import AdjustmentTypeConfig
from app.financial.variable.transaction.type.charge import ChargeTypeConfig
from app.financial.variable.transaction.type.fee import FeeTypeConfig
from app.financial.variable.transaction.type.promotion import PromotionType
from app.financial.variable.transaction.type.quantity import QuantityTypeConfig

# link http://docs.developer.amazonservices.com/en_US/finances/Finances_FeeTypes.html

TransTypeConfig = FeeTypeConfig + AdjustmentTypeConfig + ChargeTypeConfig + PromotionType + QuantityTypeConfig

FeeCategory = 'fee'
ChargeCategory = 'charge'
PromotionCategory = 'promotion'
QuantityCategory = 'quantity'

TRANS_CATEGORY_CONFIG = (
    (FeeCategory, 'Fee'),
    (ChargeCategory, 'Charge'),
    (PromotionCategory, 'Promotion'),
    (QuantityCategory, 'Quantity'),
)

ShipmentEvent = 'shipment'
RefundEvent = 'refund'
AdjustmentEvent = 'adjustment'
ServiceFeeEvent = 'service_fee'

TRANS_EVENT_CONFIG = (
    (ShipmentEvent, 'Shipment'),
    (RefundEvent, 'Refund'),
    (AdjustmentEvent, 'Adjustment'),
    (ServiceFeeEvent, 'Service Fee'),
)

# trans event list
TRANS_EVENT_LIST = [item[0] for item in TRANS_EVENT_CONFIG]
