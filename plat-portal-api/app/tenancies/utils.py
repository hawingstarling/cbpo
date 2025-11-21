from app.core.exceptions import InvalidFormatException
from itsdangerous import URLSafeTimedSerializer

from google.cloud import storage

from secrets import token_hex, choice

from string import ascii_letters, digits

from datetime import datetime

from random import randint

from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from config.settings.common import GOOGLE_CLOUD_STORAGE_BUCKET_NAME
from config.settings.common import GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY
from config.settings.common import ENVIRONMENT, SECRET_KEY

from .config_static_variable import *


class UploadImage:
    @staticmethod
    def get_extension(file):
        _, file_extension = file.name.rsplit('.', 1)
        return file_extension

    @staticmethod
    def get_blob_name(public_url):
        try:
            _, blog_name = public_url.rsplit(GOOGLE_CLOUD_STORAGE_BUCKET_NAME + '/', 1)
            return blog_name
        except Exception as ex:
            print(ex)
            return "null"

    @staticmethod
    def create_path_image(image, type_instance):
        image_extension = UploadImage.get_extension(image)
        image_name = token_hex(12) + '.' + image_extension
        now = datetime.now()
        d, m, y = now.strftime('%d'), now.strftime('%m'), now.year
        path = "%s/%s/%s/%s/%s" % (type_instance, y, m, d, image_name)
        return path

    @staticmethod
    def upload_image_to_gcloud(image, type_instance, old_image):
        path_image = UploadImage.create_path_image(image, type_instance)
        client = storage.Client.from_service_account_json(GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY)
        bucket = client.get_bucket(GOOGLE_CLOUD_STORAGE_BUCKET_NAME)
        if old_image:
            blob = bucket.blob(UploadImage.get_blob_name(old_image))
            if blob.exists() is True:
                blob.delete()

        blob = bucket.blob(path_image)
        blob.upload_from_string(image.read())
        blob.make_public()
        return blob.public_url

    @staticmethod
    def upload_image_to_local(image, type_instance, old_image):
        if old_image:
            if default_storage.exists(old_image) is True:
                default_storage.delete(old_image)
        path = "./PHOTOS/" + UploadImage.create_path_image(image, type_instance)
        path = default_storage.save(path, ContentFile(image.read()))
        return path

    @staticmethod
    def upload_image(image, type_instance, old_image=None):
        # manually, don't use settings.DEFAULT_FILE_STORAGE for gg cloud storage
        if ENVIRONMENT == 'local':
            return UploadImage.upload_image_to_local(image, type_instance, old_image)
        return UploadImage.upload_image_to_gcloud(image, type_instance, old_image)


def generate_token_otp_code(user, expired_seconds=60 * TIME_FOR_TOKEN_EXPIRED):
    try:
        s = URLSafeTimedSerializer(SECRET_KEY)
        token = s.dumps({'user_id': str(user.user_id)})
        return token
    except Exception as ex:
        print(ex)
        return None


def generate_6_digits_code():
    code = randint(100000, 999999)
    return code


def generate_random_password(pass_len=12):
    alphabet = ascii_letters + digits
    password = ''.join(choice(alphabet) for i in range(pass_len))
    return password


def get_domain_from_str_url(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return result


def validate_web_base_url(web_base_url):
        #  validate web_base_url's domain
        domain = get_domain_from_str_url(web_base_url)
        flag_domain_accepted = any(i in domain for i in WHITE_LIST_DOMAIN)
        if not flag_domain_accepted:
            raise InvalidFormatException("web_base_url's domain is invalid!")

        return web_base_url