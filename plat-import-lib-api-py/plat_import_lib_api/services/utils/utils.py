import importlib
import inspect
import os
from datetime import datetime
from secrets import token_hex
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from google.cloud import storage
from plat_import_lib_api.services.controllers.module import ModuleImportService
from plat_import_lib_api.static_variable.config import MEDIA_ROOT, plat_import_setting


def round_up_currency(value):
    try:
        value = float(value)
        _round = round(value, 2)
        _temp = _round - value
        if _temp >= 0:
            value = _round
        else:
            value = round(_round + plat_import_setting.round_up_currency, 2)
    except Exception as ex:
        pass
    return value


def normalize_map_config(map_config: list):
    try:
        return {item['target_col']: item['upload_col'] for item in map_config}
    except Exception as ex:
        return {}


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def load_lib_module(name: str, **kwargs):
    module_service = ModuleImportService(name=name, **kwargs)
    module_import = module_service.load_module()
    return module_import


def get_extension_file(file_path: str):
    file_name, file_extension = file_path.rsplit('.', 1)
    return file_name, file_extension


def create_path_file(file_path: str, module: str, category: str):
    file_name, file_extension = get_extension_file(file_path)
    file_name = token_hex(12) + '.' + file_extension

    now = datetime.now()
    d, m, y = now.strftime('%d'), now.strftime('%m'), now.year
    path = f"{plat_import_setting.storage_folder}/{module}/{category}/{y}/{m}/{d}/{file_name}"
    return path


def get_blob_name(public_url):
    try:
        _, blog_name = public_url.rsplit(plat_import_setting.google_cloud_storage_bucket_name + '/', 1)
        return blog_name
    except Exception as ex:
        print(ex)
        return "null"


def get_bucket_google_storage():
    client = storage.Client.from_service_account_json(plat_import_setting.google_cloud_storage_bucket_access_key)
    bucket = client.get_bucket(plat_import_setting.google_cloud_storage_bucket_name)
    return bucket


def delete_file_google_storage(file_path: str):
    bucket = get_bucket_google_storage()
    blob = bucket.blob(get_blob_name(file_path))
    if blob.exists() is True:
        blob.delete()


def upload_file_to_gcloud(file_path: str, module: str, category: str) -> str:
    path = create_path_file(file_path, module, category)
    bucket = get_bucket_google_storage()
    blob = bucket.blob(path)
    blob.upload_from_filename(file_path)
    blob.make_public()
    url = blob.public_url
    return url


def delete_file_local(file_path):
    if default_storage.exists(file_path) is True:
        default_storage.delete(file_path)


def upload_file_to_local(file_path: str, module: str, category: str):
    path_file = create_path_file(file_path, module, category)
    file = open(file=file_path, mode="rb")
    path = default_storage.save(path_file, ContentFile(file.read()))
    return path


def download_file_google(file_path: str, module: str, category: str):
    path_file = create_path_file(file_path, module, category)
    path_storage = os.path.join(MEDIA_ROOT, path_file)
    path_storage = default_storage.generate_filename(path_storage)
    default_storage.save(path_storage, ContentFile(''))
    # download file
    r = requests.get(file_path)
    with open(path_storage, 'wb') as f:
        f.write(r.content)
    path_storage = path_storage.replace('\\', '/')
    return path_storage


def get_modules_config_template(module_filters: [str]):
    modules = {}
    try:
        _is_all = 'all' in module_filters
        module_dir = importlib.import_module(plat_import_setting.module_template_location)
        for _class_name, _class_template in module_dir.__dict__.items():
            if inspect.isclass(_class_template):
                if not _is_all and str(_class_name) not in module_filters:
                    continue
                modules.update({_class_template.__NAME__: _class_template.__LABEL__})
    except Exception as ex:
        print(f"[get_modules_config_template] : {ex}")
    return modules
