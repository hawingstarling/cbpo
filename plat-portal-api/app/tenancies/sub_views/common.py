from app.core.logger import logger
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from app.core.exceptions import InvalidFormatException, GenericException
from ..config_app_and_module import APP_MODULE_BUILD_PROFILE
from ..config_static_variable import TYPE, TYPE_IMAGE
from app.core.utils import get_app_name_profile
from ..utils import UploadImage
from rest_framework.response import Response


class RequestLogMiddleware(object):

    def initial(self, request, *args, **kwargs):
        logger.info('API View: %s', [self.__class__.__name__])
        logger.info('API Request: %s', [request._request])
        super(RequestLogMiddleware, self).initial(request, *args, **kwargs)


class AppBaseView:

    @property
    def get_app_name_profile(self):
        return get_app_name_profile()

    @property
    def get_modules_app_profiles(self):
        return APP_MODULE_BUILD_PROFILE[self.get_app_name_profile]


class ImageUploadView(RequestLogMiddleware, APIView):
    """
    Upload image to Google Cloud Storage
    """
    parser_classes = (MultiPartParser, FormParser,)
    permission_classes = (AllowAny,)

    def get_type(self):
        type_instance = self.request.data.get('type')
        if type_instance in TYPE:
            return type_instance
        raise InvalidFormatException("The type's photo is invalid.")

    def allowed_extensions(self):
        image = self.request.data.get('file')
        image_extension = UploadImage.get_extension(image)
        if image_extension in TYPE_IMAGE:
            return
        raise InvalidFormatException('The image extension is invalid.')

    def post(self, request, *args, **kwargs):
        self.allowed_extensions()
        type_instance = self.get_type()
        try:
            image = request.data.get('file')
            old_image = request.data.get('old_image')
            path = UploadImage.upload_image(image, type_instance, old_image)
        except Exception as ex:
            print(ex)
            raise GenericException()

        return Response({'url_image': path})
