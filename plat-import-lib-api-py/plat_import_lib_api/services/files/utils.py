import os
import re
import random
import string
from datetime import timedelta
import pandas as pd
from faker import Faker
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from django.utils.datetime_safe import datetime
from plat_import_lib_api.services.utils.utils import get_bucket_google_storage
from plat_import_lib_api.static_variable.config import MEDIA_URL, BASE_URL, MEDIA_ROOT, plat_import_setting


def suggest_upload_column_to_target_column(target_cols: list, upload_cols: list):
    assert len(target_cols) > 0, "Target column is not empty"
    assert len(upload_cols) > 0, "Upload column is not empty"
    config_mapping = []
    for target in target_cols:
        regex_detector = target['name_detector']
        if not regex_detector:
            label = target['label']
            regex_detector = [f"{label}"]
        __upload_find = search_col(regex_detector, upload_cols)
        __item = {
            'target_col': target['name'],
            'upload_col': __upload_find.get('name')
        }
        config_mapping.append(__item)
    return config_mapping


def search_col(regex_detector, upload_cols):
    for regex in regex_detector:
        __find = re.compile(regex, re.IGNORECASE)
        for upload in upload_cols:
            try:
                val = __find.search(upload['label'])
                if val:
                    return upload
            except Exception as ex:
                continue
    return {}


def generate_file_path_sample(module: str, version: str = '1.0'):
    file_path = None
    module = module.lower()
    file_path = f"{plat_import_setting.storage_folder}/{module}/templates/{module}-sample-v{version}.xlsx"
    return file_path


def generate_url_sample(module: str, version: str = '1.0'):
    url = None
    file_path = generate_file_path_sample(module, version)
    if plat_import_setting.storage_location == 'local':
        file_storage = os.path.join(MEDIA_ROOT, file_path)
        url = f'{BASE_URL}{MEDIA_URL}{file_path}'
        if os.path.isfile(file_storage):
            return url, True
    if plat_import_setting.storage_location == 'google':
        url = f"https://storage.googleapis.com/{plat_import_setting.google_cloud_storage_bucket_name}/{file_path}"
        bucket = get_bucket_google_storage()
        blob = bucket.blob(file_path)
        if blob.exists():
            return url, True
    return url, False


def generate_string_and_digits(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_string(size=2, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_digits(size=2, digits=string.digits):
    return ''.join(random.choice(digits) for _ in range(size))


def prepare_data(target_cols: list, sample_data: dict, number=5):
    # make column_label_map for get label from column name (only column in sample data)
    # column_label_map = { "Brand Name": "brand"}
    column_label_map = dict()
    sample_data_columns = sample_data.keys()

    for target in target_cols:
        label = target['label']
        column_name = target['name']
        if column_name in sample_data_columns:
            column_label_map.update({column_name: label})

    data_prepared = {label: [] for label in column_label_map.values()}
    for column in column_label_map.keys():
        label = column_label_map.get(column)
        if len(sample_data[column]) == number:
            data_prepared[label] = sample_data[column]
        else:
            for i in range(number):
                data_prepared[label].append(random.choice(sample_data[column]))
    return data_prepared


def generate_file_sample(
        module,
        target_cols: list,
        version: str = 1.0,
        number: int = 5,
        sample_data: dict = None,
):
    data_prepared = {}
    if sample_data:
        data_prepared = prepare_data(target_cols, sample_data, number)

    headers = [col['label'] for col in target_cols]

    faker = Faker()
    data_rows = {}

    for target in target_cols:
        _label = target['label']
        _type = target['type']

        if data_prepared and _label in list(data_prepared.keys()):
            data_rows[_label] = data_prepared.get(_label)
            continue

        if _type == 'integer':
            _data = []
            for i in range(number):
                value = random.randint(0, 100)
                _data.append(value)
            data_rows[_label] = _data
            continue

        if _type in ['float', 'number']:
            _data = []
            for i in range(number):
                value = float("{0:.2f}".format(random.uniform(0000, 9999)))
                _data.append(value)
            data_rows[_label] = _data
            continue

        if _type == 'datetime':
            _data = []
            for i in range(number):
                value = datetime.now() - timedelta(days=i)
                _data.append(value)
            data_rows[_label] = _data
            continue

        if _type == 'boolean':
            _data = []
            for i in range(number):
                _data.append(random.choice(['True', 'False']))
            data_rows[_label] = _data
            continue

        # default no detect type generate to string
        _data = []
        for i in range(number):
            value = faker.text(max_nb_chars=10).replace('.', '')
            _data.append(value)
        data_rows[_label] = _data

    df = pd.DataFrame(data_rows, columns=headers)
    file_path = generate_file_path_sample(module, version)

    if plat_import_setting.storage_location == 'local':
        file_storage = os.path.join(MEDIA_ROOT, file_path)
        default_storage.save(file_storage, ContentFile(''))
        df.to_excel(file_storage, index=False, header=True, sheet_name='Sheet1')

    if plat_import_setting.storage_location == 'google':
        f = NamedTemporaryFile(suffix='.xlsx')
        df.to_excel(f, index=False, header=True, sheet_name='Sheet1')
        f.seek(0)
        bucket = get_bucket_google_storage()
        blob = bucket.blob(file_path)
        __GS_UPLOAD_CONTENT_TYPE__ = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        blob.upload_from_file(f, content_type=__GS_UPLOAD_CONTENT_TYPE__)
        blob.make_public()
