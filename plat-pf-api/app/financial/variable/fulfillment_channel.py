from enum import Enum


class FulfillmentChannelEnum(Enum):
    DS = "DS"
    FBA = "FBA"
    RA = "RA"
    MFN = "MFN"
    PRIME = "Prime"
    MFN_RA = "MFN-RA"
    MFN_DS = "MFN-DS"
    MFN_PRIME = "MFN-Prime"
    STORE_PRIME = "Store Prime"
    RAPID_ACCESS = "Rapid Access"
