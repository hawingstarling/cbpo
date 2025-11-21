from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from drf_yasg.utils import swagger_auto_schema
from dj_rest_auth.registration.views import SocialLoginView

from app.social_auth.serializers import CustomSocialLoginSerializer
from app.tenancies.custom_payload_jwt import custom_token_handler


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer
    callback_url = None  # dynamically
    client_class = OAuth2Client

    @swagger_auto_schema(tags=["Social Auth"])
    def post(self, request, *args, **kwargs):
        self.callback_url = request.data.get("callback_url", None)
        return super(GoogleLoginView, self).post(request, *args, **kwargs)

    def login(self):
        super(GoogleLoginView, self).login()
        #  override to append app name into JWT
        token = custom_token_handler(
            self.user, app=self.request.data.get("app")
        )
        self.token = str(token)
