
import json
from unittest.mock import patch

from django.urls import reverse


class WebhookMixin(object):
    def _get_fake_data(self, path):
        f = open(path)
        fake_data = json.load(f)
        f.close()
        return fake_data

    def _web__hook(self, fake_data_path):
        fake_data = self._get_fake_data(fake_data_path)
        url = reverse("stripe-web-hook")
        patcher = patch(
            "app.payments.services.utils.StripeApiServices.verify_data_from_event_webhook",
            return_value=fake_data,
        )
        patcher.start()
        _ = self.client.post(url, {}, format="json")  # noqa
        # self.assertEqual(response.status_code, status.HTTP_200_OK)  # noqa
        patcher.stop()
