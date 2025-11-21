import stripe as stripe_configured
from django.conf import settings

stripe_configured.api_key = settings.STRIPE_SECRET_KEY
