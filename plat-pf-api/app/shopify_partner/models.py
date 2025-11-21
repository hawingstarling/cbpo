import uuid

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from app.database.db.objects_manage import MultiDbTableManagerBase
from app.financial.models import ClientPortal


class Setting(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=256)
    # encrypted secret
    secret = models.TextField(verbose_name='secret (encrypted)')
    set_new_secret_key = models.BooleanField(default=True)
    redirect_url_oauth = models.CharField(max_length=256)
    scope = models.TextField()
    web_redirect_url = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.set_new_secret_key:
            fernet = Fernet(settings.FERNET_KEY.encode('utf-8'))
            self.secret = fernet.encrypt(self.secret.encode()).decode('utf-8')
            self.set_new_secret_key = False
        super().save(force_insert, force_update, using, update_fields)

    @property
    def get_decrypt_secret(self):
        fernet = Fernet(settings.FERNET_KEY.encode('utf-8'))
        token = self.secret.encode('utf-8')
        return fernet.decrypt(token).decode('utf-8')

    @staticmethod
    def generate_web_redirect_url(client_id: str, web_redirect_url: str) -> str:
        """
        web_redirect_url: eg: http://localhost:8080/#/pf/<client_id>/settings
        """
        return web_redirect_url.replace('<client_id>', client_id)


class OauthTokenRequest(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    shop_url = models.CharField(max_length=250)
    #
    state = models.CharField(max_length=250)
    #
    # encrypted access token
    access_token = models.TextField(null=True)
    #
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    class Meta:
        # unique by client_id and shop_url
        # supporting revoke and connect to another shop_url
        unique_together = ('client', 'shop_url',)
        indexes = [
            models.Index(fields=['client', 'shop_url'],
                         name='oauth_generate_url'),
            models.Index(fields=['state', 'shop_url'], name='callback_oauth')
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.access_token is not None:
            fernet = Fernet(settings.FERNET_KEY.encode('utf-8'))
            self.access_token = fernet.encrypt(
                self.access_token.encode()).decode('utf-8')
        return super().save(force_insert, force_update, using, update_fields)

    @property
    def get_decrypted_access_token(self) -> str:
        fernet = Fernet(settings.FERNET_KEY.encode('utf-8'))
        token = self.access_token.encode('utf-8')
        return fernet.decrypt(token).decode('utf-8')


class ShopifyPartnerOauthClientRegister(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #
    client = models.ForeignKey(ClientPortal, on_delete=models.CASCADE)
    oauth_token_request = models.ForeignKey(
        OauthTokenRequest, on_delete=models.CASCADE)
    #
    enabled = models.BooleanField(default=False)
    objects = MultiDbTableManagerBase()
    all_objects = MultiDbTableManagerBase()

    def __str__(self):
        return f"{self.client} - {self.oauth_token_request.shop_url} - {self.enabled}"

    class Meta:
        unique_together = ['client', 'oauth_token_request']
        indexes = [
            models.Index(fields=['client', 'oauth_token_request']),
            models.Index(fields=['client', 'enabled'])
        ]
