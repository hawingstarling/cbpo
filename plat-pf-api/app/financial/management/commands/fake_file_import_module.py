import os
import random
import string
import time
from datetime import datetime, timedelta
from secrets import token_hex
import numpy
import pandas as pd
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from faker import Faker
from plat_import_lib_api.services.utils.utils import load_lib_module
from app.financial.models import Brand
from app.financial.variable.profit_status_static_variable import PROFIT_STATUS
from app.financial.variable.sale_status_static_variable import SALE_STATUS
from plat_import_lib_api.static_variable.config import plat_import_setting


class Command(BaseCommand):
    help = "Help make fake data sale items large data for check."

    @staticmethod
    def columns(module: str):
        """
        Columns name define in module
        :return:
        """
        serializer = load_lib_module(name=module)
        return serializer.columns

    @classmethod
    def chunks_number(cls, numbers: int = 2000, segment: int = 5):
        x = range(numbers)
        return numpy.array_split(numpy.array(x), segment)

    def generate_string_and_digits(self, size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def generate_string(self, size=2, chars=string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def generate_digits(self, size=2, digits=string.digits):
        return ''.join(random.choice(digits) for _ in range(size))

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, help='Number record fake data')
        parser.add_argument('-m', '--module', type=str, help='Name module provide for fake data')

    def handle(self, *args, **options):
        print("--------Start generate fake data export file-------------")
        number = options.get('number', 1000)
        module = options.get('module', None)
        if not module:
            print("Module is not None . Pls using python manage.py fake_data_to_module_to_file --help get more info")
            return

        info_generate = {'module': module, 'number': number, 'url': None}

        start_time = time.time()
        #
        df = self.generate_data_to_excel(number, module)

        path_file = f"{plat_import_setting.storage_folder}/fake_data/{module}/template-data-{module}-{number}-{token_hex(10)}.xlsx"

        path_storage = os.path.join(settings.MEDIA_ROOT, path_file)
        path_storage = default_storage.generate_filename(path_storage)
        default_storage.save(path_storage, ContentFile(''))
        df.to_excel(path_storage, index=False, header=True)

        url = f'{settings.BASE_URL}{settings.MEDIA_URL}{path_file}'

        end_time = time.time()
        time_exec = end_time - start_time

        info_generate.update({'url': url, 'time_exec': time_exec})
        print(f"info: {info_generate}")

    def data_prepare(self, number, module: str):
        _style = ['Blue', 'Red', 'Brown', 'Spring', 'Winter', 'Summer', 'Holiday']
        _size = ['M', 'L', 'XL']
        _channel = ['amazon.com', 'amazon.com', 'amazon.com']
        _fulfillment_type = ['MFN', 'FBA']
        _brand_name = Brand.objects.all().values_list('name', flat=True).distinct()
        _address_line_1 = ['590 TREETOP LN', '590 TREETOP LN', '590 TREETOP LN']
        _address_line_2 = ['1130 BROADWAY ST', '1130 BROADWAY ST', '1130 BROADWAY ST']
        _address_line_3 = ['1991 HIGH DR', '1991 HIGH DR', '1991 HIGH DR']
        _customer_name = ['Jess', 'Jess', 'Jess']

        address_info = {
            'New York': ['New York City'],
            'California': ['Los Angeles', 'San Diego'],
            'Texas': ['Houston', 'San Antonio'],
            'Arizona': ['Phoenix'],
            'Pennsylvania': ['Philadelphia'],
            'Florida': ['Jacksonville']
        }

        # data init
        channel = []
        channel_sale_id = []
        sku = []
        upc = []
        asin = []
        style = []
        size = []
        fulfillment_type = []
        state = []
        city = []
        country = []
        postal_code = []
        brand = []
        shipping_cost_accuracy = []
        channel_listing_fee_accuracy = []
        sale_charged_accuracy = []
        cog = []
        unit_cog = []
        quantity = []

        _state_list = list(address_info.keys())

        for i in range(number):
            channel.append(random.choice(_channel))
            channel_sale_id.append(
                '{}-{}-{}{}'.format(self.generate_string(3), self.generate_digits(3), self.generate_string(2),
                                    self.generate_digits(2)))
            brand.append(random.choice(_brand_name))
            #
            sku.append(
                '{}_{}-{}_{}-{}'.format(self.generate_string(2), self.generate_digits(2), self.generate_digits(5),
                                        self.generate_digits(1), self.generate_string(1)))
            upc.append(self.generate_digits(random.choice([12, 13])))
            #
            asin.append(self.generate_string_and_digits())
            #
            style.append(random.choice(_style))
            #
            size.append(random.choice(_size))

            _state = random.choice(_state_list)
            state.append(_state)
            _city = random.choice(address_info[_state])
            city.append(_city)
            country.append('USA')
            postal_code.append(str(f"{self.generate_digits(4)}-{self.generate_digits(5)}"))

            fulfillment_type.append(random.choice(_fulfillment_type))

            shipping_cost_accuracy.append(100)
            channel_listing_fee_accuracy.append(100)
            sale_charged_accuracy.append(100)

            cog.append(10)
            unit_cog.append(5)
            quantity.append(2)
        #
        return {
            'Channel Sale ID': channel_sale_id,
            'Channel': channel,
            'Brand': brand,
            'SKU': sku,
            'UPC': upc,
            'ASIN': asin,
            'Style Variant': style,
            'Size Variant': size,
            'Fulfillment Type': fulfillment_type,
            'State': state,
            'City': city,
            'Postal Code': postal_code,
            'Country': country,
            'Shipping Cost Accuracy': shipping_cost_accuracy,
            'Sale Charged Accuracy': sale_charged_accuracy,
            'Channel Listing Fee Accuracy': channel_listing_fee_accuracy,
            'COG': cog,
            'Unit COG': unit_cog,
            'Quantity': quantity,
            'Customer Name': _customer_name,
            'Address Line 1': _address_line_1,
            'Address Line 2': _address_line_2,
            'Address Line 3': _address_line_3,
        }

    def generate_data_to_excel(self, number, module):

        sale_status = [item[0][0] for item in SALE_STATUS]

        profit_status = [item[0][0] for item in PROFIT_STATUS]

        faker = Faker()
        data_rows = {}
        #
        target_cols = self.columns(module)

        data_prepare = self.data_prepare(number, module)

        # generate headers
        headers = [col['label'] for col in target_cols]

        print(f"Column module template : {headers}")

        # generate data
        for col in target_cols:
            label = col['label']
            type_col = col['type']
            _data = []
            if label in list(data_prepare.keys()):
                data_rows[label] = data_prepare.get(label)
                continue
            if type_col == 'datetime':
                for i in range(number):
                    value = datetime.now() - timedelta(days=i)
                    _data.append(value)
                data_rows[label] = _data
                continue
            # sale status
            if col['label'] in ['Sale Status']:
                for i in range(number):
                    _data.append(random.choice(sale_status))
                data_rows[label] = _data
                continue
            # profit status
            if col['label'] in ['Profit Status']:
                for i in range(number):
                    _data.append(random.choice(profit_status))
                data_rows[label] = _data
                continue
            if type_col == "string":
                for i in range(number):
                    value = faker.text(max_nb_chars=10).replace('.', '')
                    _data.append(value)
                data_rows[label] = _data
                continue
            if type_col == "integer":
                for i in range(number):
                    _data.append(random.randint(0, 100))
                data_rows[label] = _data
                continue

            if type_col == "float" or type_col == "number":
                for i in range(number):
                    value = float("{0:.2f}".format(random.uniform(0, 9999)))
                    _data.append(value)
                data_rows[label] = _data
                continue

            if type_col == "boolean":
                for i in range(number):
                    _data.append(random.choice([True, False]))
                data_rows[label] = _data
                continue

        # for key in data_rows.keys():
        #     print(key, len(data_rows[key]))

        df = pd.DataFrame(data_rows, columns=headers)
        return df
