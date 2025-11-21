import copy
import datetime
import random
import string
from datetime import date

from faker import Faker

LIMIT_SIZE = 1000

_date_now = date.today().strftime('%Y-%m-%d')

LIVE_FEED_STATUS = {
    "marketplace": "ATVPDKIKX0DER",
    "modified_date": _date_now,
    "ready": True
}

SC_LIVE_FEED_AMAZON_US = {
    "total": 4,
    "page_count": 1,
    "page_size": LIMIT_SIZE,
    "page_current": 1,
    "items": [
        {
            "channel_sale_id": "111-222-3334",
            "channel": "amazon.com",
            "sale_date": "2020-01-01 00:00:00",
            "asin": "BR12345700",
            "title": "test sync live feed",
            "sku": "AL-DAT-3233",
            "brand_sku": None,
            "quantity": 1,
            "sale_charged": None,
            "sale_charged_est": 1.0,
            "shipping_charged": 1.5,
            "tax_charged": 1.5,
            "shipping_cost": 1.5,
            "tax_cost": 1.5,
            "ship_date": None,
            "sale_status": "Pending",
            "profit_status": "Projected",
            "channel_listing_fee": 1.5,
            "other_channel_fees": 1.5,
            "fulfillment_type": "FBA",
            "notes": None,
            "city": "Inyo County",
            "state": "LA",
            "country": "United States",
            "postal_code": "11111-2222",
            "is_prime": True,
            "customer_name": "Test",
            "recipient_name": "TestTest",
            "address_line": {
                "address_line_1": "123 Main St",
                "address_line_2": None,
                "address_line_3": None
            },
            "packages": [{
                "tracking_id": "1234567890",
                "ship_date": "2021/11/21",
                "ship_carrier": "ship_carrier",
                "ship_service": "ship_service",
                "ship_label": 155.5,
                "ship_total": 14,
            }],
            "label_cost": 1.0,
            "label_type": "AmazonPrePaidLabel"
        },
        {
            "channel_sale_id": "111-222-3334",
            "channel": "amazon.com",
            "sale_date": "2020-01-01 00:00:00",
            "asin": "BR12345700",
            "title": "test sync live feed",
            "sku": "AL-DAT-2234",
            "brand_sku": None,
            "quantity": 1,
            "sale_charged": None,
            "sale_charged_est": 1.0,
            "shipping_charged": 1.5,
            "tax_charged": 1.5,
            "shipping_cost": 1.5,
            "tax_cost": 1.5,
            "ship_date": None,
            "sale_status": "Completed",
            "profit_status": "Final",
            "channel_listing_fee": 1.5,
            "other_channel_fees": 1.5,
            "fulfillment_type": "MFN",
            "notes": None,
            "city": "Inyo County",
            "state": "LA",
            "country": "United States",
            "postal_code": "11111-2222",
            "is_prime": True,
            "customer_name": "Test",
            "recipient_name": "TestTest",
            "address_line": {
                "address_line_1": "123 Main St",
                "address_line_2": None,
                "address_line_3": None
            },
            "packages": [{
                "tracking_id": "1234567890",
                "ship_date": "2021/11/21",
                "ship_carrier": "ship_carrier",
                "ship_service": "ship_service",
                "ship_label": 155.5,
                "ship_total": 14,
            }],
            "label_cost": 1.0,
            "label_type": "AmazonPrePaidLabel"
        },
        {
            "channel_sale_id": "111-222-3338",
            "channel": "amazon.com",
            "state": "LA",
            "sale_date": "2020-01-01 00:00:00",
            "asin": "BR12345700",
            "title": None,
            "sku": "AL-DAT-3239",
            "brand_sku": None,
            "quantity": 1,
            "sale_charged": -1.5,
            "shipping_charged": 1.5,
            "sale_charged_est": None,
            "tax_charged": 1.5,
            "shipping_cost": 1.5,
            "tax_cost": 1.5,
            "ship_date": None,
            "sale_status": None,
            "profit_status": None,
            "channel_listing_fee": 1.5,
            "other_channel_fees": 1.5,
            "fulfillment_type": "FBA",
            "notes": None
        },
        {
            "channel_sale_id": "111-222-3350",
            "channel": "",
            "state": "LA",
            "sale_date": "2020-01-01 00:00:00",
            "asin": "BR12345700",
            "title": "test sync live feed",
            "sku": "AL-DAT-3250",
            "brand_sku": None,
            "quantity": 1,
            "sale_charged": 1.5,
            "sale_charged_est": None,
            "shipping_charged": 1.5,
            "tax_charged": 1.5,
            "shipping_cost": 1.5,
            "tax_cost": 1.5,
            "ship_date": None,
            "sale_status": None,
            "profit_status": None,
            "channel_listing_fee": 1.5,
            "other_channel_fees": 1.5,
            "fulfillment_type": "MFN",
            "notes": None
        }
    ]
}

# FAKE DATA LIVE FEED BY SELLER_PARTNER_CONNECTION
TEMPLATE_AC_ROW = {
    "channel_sale_id": "{}",
    "channel": "amazon.com",
    "sale_date": "{}",
    "asin": "{}",
    "title": "{}",
    "sku": "{}",
    "brand_sku": None,
    "quantity": 1,
    "sale_charged": 1.5,
    "sale_charged_est": 1.0,
    "shipping_charged": 1.5,
    "tax_charged": 1.5,
    "shipping_cost": 1.5,
    "tax_cost": 1.5,
    "ship_date": None,
    "sale_status": None,
    "profit_status": None,
    "channel_listing_fee": 1.5,
    "other_channel_fees": 1.5,
    "fulfillment_type": "FBA",
    "notes": None,
    "city": "Inyo County",
    "state": "LA",
    "country": "United States",
    "postal_code": "11111-2222",
    "customer_name": "Test",
    "recipient_name": "TestTest",
    "address_line": {
        "address_line_1": "123 Main St",
        "address_line_2": None,
        "address_line_3": None
    },
    "packages": [{
        "tracking_id": "1234567890",
        "ship_date": "2021/11/21",
        "ship_carrier": "ship_carrier",
        "ship_service": "ship_service",
        "ship_label": 155.5,
        "ship_total": 14,
    }]
}


def generate_string_and_digits(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_string(size):
    chars = string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(size))


def generate_digits(size=2, digits=string.digits):
    return ''.join(random.choice(digits) for _ in range(size))


faker = Faker()

_style = ['Blue', 'Red', 'Brown', 'Spring', 'Winter', 'Summer', 'Holiday']
_size = ['M', 'L', 'XL']

sale_date_date_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def fake_sc_data_live_feed(marketplace: str = 'amazon.com', number: int = 5):
    data = []

    for i in range(number):
        item = copy.deepcopy(TEMPLATE_AC_ROW)
        item['marketplace'] = marketplace
        item['channel_sale_id'] = '{}-{}-{}{}'.format(generate_string(3), generate_digits(3), generate_string(2),
                                                      generate_digits(2))
        # item['state'] = faker.text(max_nb_chars=10).replace('.', '')
        item['sale_date'] = sale_date_date_time
        item['asin'] = generate_string_and_digits()
        item['title'] = faker.text(max_nb_chars=10).replace('.', '')
        item['sku'] = '{}_{}-{}_{}-{}'.format(generate_string(2), generate_digits(2), generate_digits(5),
                                              generate_digits(1), generate_string(1))
        data.append(item)
    return data


def get_data_fake_live_feed_marketplace(marketplace: str = 'amazon.com', number: int = 5):
    return {
        "total": number,
        "page_count": 1,
        "page_size": LIMIT_SIZE,
        "page_current": 1,
        "items": fake_sc_data_live_feed(marketplace=marketplace, number=number)
    }
