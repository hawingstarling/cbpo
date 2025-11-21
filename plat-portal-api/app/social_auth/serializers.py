import json

from allauth.account import app_settings as allauth_settings
from allauth.socialaccount.helpers import complete_social_login
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from requests.exceptions import HTTPError
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers

from app.social_auth.exceptions import ValueAPIException
from app.tenancies.config_app_and_module import APP_BUILD_TRANSIT, APP_BUILD_MWRW
from app.tenancies.models import WhiteListEmail

message = "User is already registered with this e-mail address. Confirm for getting an association"


def custom_hook_register_user(app_name, user):
    if app_name in [APP_BUILD_TRANSIT, APP_BUILD_MWRW]:
        user.can_create_client = True
        return user

    # TODO apps

    return user


def validate_social_account_for_apps(app_name, user):
    if app_name == APP_BUILD_TRANSIT:
        if settings.ONLY_ALLOW_REGISTRATION_FOR_WHITE_LISTED_EMAILS:
            try:
                WhiteListEmail.objects.get(email=user.email)
            except WhiteListEmail.DoesNotExist:
                raise serializers.ValidationError(
                    detail={
                        "email": "The email is not in the white list for registration"
                    },
                    code="invalid",
                )
    # TODO Apps


class CustomSocialLoginSerializer(SocialLoginSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    app = serializers.CharField(required=False)
    callback_url = serializers.URLField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_email(self, value):  # noqa
        # checking white list of email for registration transit app
        # invitation -> bypass
        if settings.ONLY_ALLOW_REGISTRATION_FOR_WHITE_LISTED_EMAILS:
            try:
                WhiteListEmail.objects.get(email=value)
                return value
            except WhiteListEmail.DoesNotExist:
                raise serializers.ValidationError(
                    "The email is not in the white list for registration"
                )
        return value

    def validate_callback_url(self, value):  # noqa
        with open(settings.CREDENTIAL_GOOGLE_AUTH_PATH) as f:
            data = json.load(f)
            web = data.get("web", {})
            valid_domains = web.get("redirect_uris", [])
            if not len(valid_domains):
                raise Exception("requires redirect_uris configuration.")
            if value not in valid_domains:
                raise serializers.ValidationError(f"{value} is an invalid callback url")
            return value

    def validate(self, attrs):
        """
        override validation
        @param attrs:
        @return:
        """
        view = self.context.get("view")
        request = self._get_request()

        """----- custom -----"""
        local_account_email = attrs.get("email", None)
        local_account_password = attrs.get("password", None)
        is_valid_confirm_local_account = False

        if local_account_email is not None and local_account_password is not None:
            login_confirm_serializer = LoginSerializer(
                data={"email": local_account_email, "password": local_account_password},
                context={"request": request},
            )
            login_confirm_serializer.is_valid(raise_exception=True)
            is_valid_confirm_local_account = True
        """----- custom -----"""

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        # Case 1: We received the access_token
        if attrs.get("access_token"):
            access_token = attrs.get("access_token")

        # Case 2: We received the authorization code
        elif attrs.get("code"):
            self.callback_url = getattr(view, "callback_url", None)
            self.client_class = getattr(view, "client_class", None)

            if not self.callback_url:
                raise serializers.ValidationError(_("Define callback_url in view"))
            if not self.client_class:
                raise serializers.ValidationError(_("Define client_class in view"))

            code = attrs.get("code")

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
            )
            token = client.get_access_token(code)
            access_token = token["access_token"]

        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required.")
            )

        social_token = adapter.parse_token({"access_token": access_token})
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            if not login.is_existing:
                # custom validate for apps
                validate_social_account_for_apps(
                    app_name=self.initial_data.get("app", None), user=login.user
                )
                # custom user register for apps
                login.user = custom_hook_register_user(
                    app_name=self.initial_data.get("app", None), user=login.user
                )
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                """----- custom -----"""
                account_exists_list = get_user_model().objects.filter(
                    email=login.user.email,
                )
                if account_exists_list.exists():
                    if not is_valid_confirm_local_account:
                        raise ValueAPIException(
                            {
                                "access_token": access_token,
                                "message": _(message),
                                "email": login.user.email,
                            }
                        )
                    else:
                        login.user = account_exists_list[0]
                """----- custom -----"""

            login.lookup()
            login.save(request, connect=True)

        attrs["user"] = login.account.user

        return attrs
