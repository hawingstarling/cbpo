import csv
import datetime
import os
import random
import string
import time
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.utils import timezone
from plat_import_lib_api.static_variable.config import plat_import_setting


class Command(BaseCommand):
    help = "Help make fake data sale items large data for check."

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.date_range_random = [
            datetime.datetime(day=8, month=5, year=2023),
            datetime.datetime(day=7, month=5, year=2023),
            datetime.datetime(day=6, month=5, year=2023),
            datetime.datetime(day=5, month=5, year=2023),
            datetime.datetime(day=4, month=5, year=2023),
            datetime.datetime(day=3, month=5, year=2023),
            datetime.datetime(day=2, month=5, year=2023),
            datetime.datetime(day=1, month=5, year=2023),
            datetime.datetime(day=30, month=4, year=2023),
            datetime.datetime(day=29, month=4, year=2023)
        ]

        self.quantity_random = [
            10,
            20,
            30,
            44,
            55,
            66,
            70,
            80,
            90,
            150
        ]

        self.values_random = [
            120.00,
            230.00,
            340.00,
            450.00,
            560.00,
            670.00,
            780.00,
            890.00,
            990.00,
        ]

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, help='Number record fake data')
        parser.add_argument('-b', '--brand', type=str, help='Name brand provide for fake data')

    def handle(self, *args, **options):
        print("--------Start generate fake data dd export file-------------")
        number = options.get('number', 1000)
        brand = options.get('brand', None)
        if not brand:
            print("Brand is not None . Pls using python manage.py fake_data_to_module_to_file --help get more info")
            return

        header = ['SKU', 'ReportDate', 'Brand', 'Quantity', 'Days7Sales', 'Days30Sales', 'Days90Sales']

        info_generate = {'module': brand, 'number': number, 'url': None}

        start_time = time.time()
        #
        time_now = timezone.now()
        d, m, y = time_now.strftime('%d'), time_now.strftime('%m'), time_now.year
        timestamp = int(time_now.timestamp())
        file_path = f"{plat_import_setting.storage_folder}/dd_reports//{y}/{m}/{d}/{brand}-{timestamp}.csv"
        file_storage = os.path.join(settings.MEDIA_ROOT, file_path)
        file_storage = default_storage.save(file_storage, ContentFile(''))
        with open(file_storage, 'w', newline='') as f:
            w = csv.writer(f)

            w.writerow(header)

            for i in range(number):
                data = self.prepare_data_rows(i, brand)
                w.writerow(data)

        url = f'{settings.BASE_URL}{settings.MEDIA_URL}{file_path}'

        end_time = time.time()
        time_exec = end_time - start_time

        info_generate.update({'url': url, 'time_exec': time_exec})
        print(f"info: {info_generate}")

    @staticmethod
    def generate_string(size=2, chars=string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def generate_digits(size=2, digits=string.digits):
        return ''.join(random.choice(digits) for _ in range(size))

    def prepare_data_rows(self, number: int, brand: str):
        sku = '{}_{}-{}_{}-{}'.format(self.generate_string(2), self.generate_digits(2), self.generate_digits(5),
                                      self.generate_digits(1), self.generate_string(1))
        data = [
            sku,
            random.choice(self.date_range_random),
            brand,
            random.choice(self.quantity_random),
            random.choice(self.values_random),
            random.choice(self.values_random),
            random.choice(self.values_random)
        ]
        return data
