from datetime import date

_date_now = date.today().strftime('%Y-%m-%d')

TRANS_EVENT_STATUS = {
    "marketplace": "ATVPDKIKX0DER",
    "posted_date": _date_now,
    "ready": True
}

TRANS_EVENT = {
    "total": 1,
    "page_count": 1,
    "page_size": 100,
    "page_current": 1,
    "items": [
        {
            "amazon_order_id": "111-222-3336",
            "marketplace": "amazon.com",
            "modified": "2020-09-19T05:18:16.350Z",
            "shipment_event": {
                "ShipmentItemList": {
                    "ShipmentItem": {
                        "ItemTaxWithheldList": {
                            "TaxWithheldComponent": {
                                "TaxCollectionModel": "MarketplaceFacilitator",
                                "TaxesWithheld": {
                                    "ChargeComponent": [
                                        {
                                            "ChargeType": "MarketplaceFacilitatorTax-Shipping",
                                            "ChargeAmount": {
                                                "CurrencyAmount": "0.0",
                                                "CurrencyCode": "USD"
                                            }
                                        },
                                        {
                                            "ChargeType": "MarketplaceFacilitatorTax-Principal",
                                            "ChargeAmount": {
                                                "CurrencyAmount": "-1",
                                                "CurrencyCode": "USD"
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        "ItemChargeList": {
                            "ChargeComponent": [
                                {
                                    "ChargeType": "Principal",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "88.95",
                                        "CurrencyCode": "USD"
                                    }
                                },
                                {
                                    "ChargeType": "Tax",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "5.5",
                                        "CurrencyCode": "USD"
                                    }
                                },
                                {
                                    "ChargeType": "GiftWrap",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    }
                                },
                                {
                                    "ChargeType": "GiftWrapTax",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "1.1",
                                        "CurrencyCode": "USD"
                                    }
                                },
                                {
                                    "ChargeType": "ShippingCharge",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    }
                                },
                                {
                                    "ChargeType": "ShippingTax",
                                    "ChargeAmount": {
                                        "CurrencyAmount": "1.1",
                                        "CurrencyCode": "USD"
                                    }
                                }
                            ]
                        },
                        "ItemFeeList": {
                            "FeeComponent": [
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "-13.34",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "Commission"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "FixedClosingFee"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "GiftwrapCommission"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "SalesTaxCollectionFee"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "ShippingHB"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "VariableClosingFee"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "-1.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "FBAPerUnitFulfillmentFee"
                                },
                                {
                                    "FeeAmount": {
                                        "CurrencyAmount": "-1.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "FeeType": "FBAPerOrderFulfillmentFee"
                                }
                            ]
                        },
                        "OrderItemId": "49613271055394",
                        "QuantityShipped": "1",
                        "SellerSKU": "AL-DAT-2236",
                        "PromotionList": {
                            "Promotion": [
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                },
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                },
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                },
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                },
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "-9.29",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                },
                                {
                                    "PromotionType": "PromotionMetaDataDefinitionValue",
                                    "PromotionAmount": {
                                        "CurrencyAmount": "0.0",
                                        "CurrencyCode": "USD"
                                    },
                                    "PromotionId": "US Core Free Shipping Promotion A3JU1FCINF5SD0"
                                }
                            ]
                        }
                    }
                },
                "AmazonOrderId": "111-222-3336",
                "PostedDate": "2020-08-27T19:09:02.015Z",
                "MarketplaceName": "Amazon.com"
            },
            "refund_event": [
                {
                    "AmazonOrderId": "111-222-3336",
                    "PostedDate": "2020-09-17T00:58:41.961Z",
                    "ShipmentItemAdjustmentList": {
                        "ShipmentItem": {
                            "ItemTaxWithheldList": {
                                "TaxWithheldComponent": {
                                    "TaxCollectionModel": "MarketplaceFacilitator",
                                    "TaxesWithheld": {
                                        "ChargeComponent": {
                                            "ChargeType": "MarketplaceFacilitatorTax-Principal",
                                            "ChargeAmount": {
                                                "CurrencyAmount": "1.0",
                                                "CurrencyCode": "USD"
                                            }
                                        }
                                    }
                                }
                            },
                            "ItemFeeAdjustmentList": {
                                "FeeComponent": [
                                    {
                                        "FeeAmount": {
                                            "CurrencyAmount": "13.34",
                                            "CurrencyCode": "USD"
                                        },
                                        "FeeType": "Commission"
                                    },
                                    {
                                        "FeeAmount": {
                                            "CurrencyAmount": "-2.67",
                                            "CurrencyCode": "USD"
                                        },
                                        "FeeType": "RefundCommission"
                                    }
                                ]
                            },
                            "OrderAdjustmentItemId": "49613271055394",
                            "QuantityShipped": "1",
                            "ItemChargeAdjustmentList": {
                                "ChargeComponent": [
                                    {
                                        "ChargeType": "Tax",
                                        "ChargeAmount": {
                                            "CurrencyAmount": "0.0",
                                            "CurrencyCode": "USD"
                                        }
                                    },
                                    {
                                        "ChargeType": "Principal",
                                        "ChargeAmount": {
                                            "CurrencyAmount": "-88.95",
                                            "CurrencyCode": "USD"
                                        }
                                    }
                                ]
                            },
                            "SellerSKU": "AL-DAT-2236"
                        }
                    },
                    "MarketplaceName": "Amazon.com"
                },
                {
                    "AmazonOrderId": "114-1203720-5521815",
                    "PostedDate": "2020-12-20T23:39:07.915Z",
                    "ShipmentItemAdjustmentList": {
                        "ShipmentItem": {
                            "ItemTaxWithheldList": {
                                "TaxWithheldComponent": {
                                    "TaxCollectionModel": "MarketplaceFacilitator",
                                    "TaxesWithheld": {
                                        "ChargeComponent": {
                                            "ChargeType": "MarketplaceFacilitatorTax-Principal",
                                            "ChargeAmount": {
                                                "CurrencyAmount": "0.0",
                                                "CurrencyCode": "USD"
                                            }
                                        }
                                    }
                                }
                            },
                            "ItemFeeAdjustmentList": {
                                "FeeComponent": [
                                    {
                                        "FeeAmount": {
                                            "CurrencyAmount": "13.47",
                                            "CurrencyCode": "USD"
                                        },
                                        "FeeType": "Commission"
                                    },
                                    {
                                        "FeeAmount": {
                                            "CurrencyAmount": "-2.69",
                                            "CurrencyCode": "USD"
                                        },
                                        "FeeType": "RefundCommission"
                                    }
                                ]
                            },
                            "OrderAdjustmentItemId": "33790084000226",
                            "QuantityShipped": "1",
                            "ItemChargeAdjustmentList": {
                                "ChargeComponent": [
                                    {
                                        "ChargeType": "Tax",
                                        "ChargeAmount": {
                                            "CurrencyAmount": "0.0",
                                            "CurrencyCode": "USD"
                                        }
                                    },
                                    {
                                        "ChargeType": "Principal",
                                        "ChargeAmount": {
                                            "CurrencyAmount": "-89.79",
                                            "CurrencyCode": "USD"
                                        }
                                    }
                                ]
                            },
                            "SellerSKU": "AT-AL0A4PE8-210-11"
                        }
                    },
                    "MarketplaceName": "Amazon.com",
                    "SellerOrderId": "114-1203720-5521815"
                }
            ],
            "adjustment_event": {
                "AdjustmentEvent": [
                    {
                        "AdjustmentType": "REVERSAL_REIMBURSEMENT",
                        "AdjustmentItemList": {
                            "AdjustmentItem": {
                                "PerUnitAmount": {
                                    "CurrencyAmount": "68.76",
                                    "CurrencyCode": "USD"
                                },
                                "TotalAmount": {
                                    "CurrencyAmount": "68.76",
                                    "CurrencyCode": "USD"
                                },
                                "Quantity": "1",
                                "SellerSKU": "AL-DAT-2236",
                                "ProductDescription": "Saucony Men&apos;s Omni ISO 2 Running Shoe, Blue/Silver, 9 Wide"
                            }
                        },
                        "AdjustmentAmount": {
                            "CurrencyAmount": "68.76",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "PostageBilling_TransactionFee",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "0.0",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "PostageBilling_Postage",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-8.14",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    # Add record for adjustment type PostageBilling_Postage for check duplicate case
                    {
                        "AdjustmentType": "PostageBilling_Postage",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-8.14",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "PostageBilling_DeliveryConfirmation",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "0.0",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "ReturnPostageBilling_Tracking",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "0.0",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "Other",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "0.0",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "ReturnPostageBilling_Postage",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-9.29",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "ReturnPostageBilling_FuelSurcharge",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-0.65",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "ReturnPostageBilling_OversizeSurcharge",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-0.25",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                    {
                        "AdjustmentType": "ReturnPostageBilling_DeliveryAreaSurcharge",
                        "AdjustmentAmount": {
                            "CurrencyAmount": "-0.35",
                            "CurrencyCode": "USD"
                        },
                        "PostedDate": "2020-09-03T10:02:53.626Z"
                    },
                ],
            },
            "service_fee_event": {
                "FeeDescription": "B Belleville Arm Your Feet Men&apos;s C390 Hot Weather Combat Boot, Coyote - 8.5 W",
                "AmazonOrderId": "111-222-3336",
                "SellerSKU": "AL-DAT-2236",
                "FeeList": {
                    "FeeComponent": [
                        {
                            "FeeAmount": {
                                "CurrencyAmount": "0.0",
                                "CurrencyCode": "USD"
                            },
                            "FeeType": "FBACustomerReturnPerOrderFee"
                        },
                        {
                            "FeeAmount": {
                                "CurrencyAmount": "-7.32",
                                "CurrencyCode": "USD"
                            },
                            "FeeType": "FBACustomerReturnPerUnitFee"
                        },
                        {
                            "FeeAmount": {
                                "CurrencyAmount": "0.0",
                                "CurrencyCode": "USD"
                            },
                            "FeeType": "FBACustomerReturnWeightBasedFee"
                        }
                    ]
                }
            }
        }
    ]
}
