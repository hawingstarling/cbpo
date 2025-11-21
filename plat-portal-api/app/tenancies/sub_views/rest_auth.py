from dj_rest_auth.serializers import TokenSerializer
from dj_rest_auth.utils import default_create_token
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.registration.views import RegisterView
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.tenancies.config_app_and_module import APP_BUILD_TRANSIT, APP_BUILD_MWRW
from app.tenancies.serializers import (
    AppJSONWebTokenSerializer,
    ChaneEmailSerializer,
    ChangeEmailConfirmSerializer,
    CustomRefreshJSONWebTokenSerializer,
    PasswordResetSerializer,
    UserRegisterActivationSerializer,
    UserReSendActivationCodeSerializer,
    UserResetPasswordIdentitySerializer,
)

from .common import RequestLogMiddleware


class ChangeEmailView(APIView):
    """
    Change email user
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ChaneEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # create code and send to the email
        serializer.send_email_code(self.request.user)
        return Response(
            {"message": "A 6 digit verification code has been sent to your email!"},
            status=status.HTTP_200_OK,
        )


class ChangeEmailConfirmView(generics.UpdateAPIView):
    """
    Confirm change email user
    """

    serializer_class = ChangeEmailConfirmSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.perform_save()


class UserRegisterActivationView(generics.UpdateAPIView):
    """ "
    User Activation
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserRegisterActivationSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Activate successfully."}, status=status.HTTP_200_OK
        )


class UserReSendActivationCodeView(RequestLogMiddleware, APIView):
    """
    Re-send code for activation user
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserReSendActivationCodeSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class()
        serializer.is_activated(self.request.user)
        # create and send code to email for activation
        serializer.send_email_code(self.request.user)
        return Response(
            {"message": "Re-send activation code successfully."},
            status=status.HTTP_200_OK,
        )


class CustomRegisterView(RequestLogMiddleware, RegisterView):
    """
    Register new user
    """

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        default_create_token(self.token_model, user, serializer)
        serializer.send_email_activation(user)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        if serializer.validated_data.get("app", "") in [APP_BUILD_TRANSIT, APP_BUILD_MWRW]:
            user.can_create_client = True
            user.save()
        headers = self.get_success_headers(serializer.data)
        token = TokenSerializer(user.auth_token).data

        return Response(token, status=status.HTTP_201_CREATED, headers=headers)


class PasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class CustomPasswordResetView(RequestLogMiddleware, PasswordResetView):
    """
    Custom Password Recovery From Rest Auth
    """

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        token = serializer.get_token()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset e-mail has been sent."), "token": token},
            status=status.HTTP_200_OK,
        )


class UserResetPasswordIdentityView(RequestLogMiddleware, APIView):
    """
    user identity by code, token
    """

    permission_classes = (AllowAny,)
    serializer_class = UserResetPasswordIdentitySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.advanced_validation()
        token = serializer.get_token(user)
        return Response({"token": token}, status=status.HTTP_200_OK)


class AppLoginView(TokenObtainPairView):
    serializer_class = AppJSONWebTokenSerializer


class CustomRefreshJSONWebTokenView(RequestLogMiddleware, TokenRefreshView):
    """
    API View that returns a refreshed token (with new expiration) based on
    existing token
    If 'orig_iat' field (original issued-at-time) is found, will first check
    if it's within expiration window, then copy it to the new token
    """

    serializer_class = CustomRefreshJSONWebTokenSerializer
