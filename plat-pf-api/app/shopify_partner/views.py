from django.shortcuts import render
from django.views import generic

from app.shopify_partner.static_setting import SHOPIFY_CTX_REQUIRED_REGISTER_SHOP_URL


class ShopifyIntegrationIndexView(generic.base.View):
    template_name = 'shopify/shopify_integration_message.html'

    def get(self, request, *args, **kwargs):
        context = SHOPIFY_CTX_REQUIRED_REGISTER_SHOP_URL
        return render(request, self.template_name, context=context)
