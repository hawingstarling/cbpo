from django.contrib import admin

# from app.core.admin.client_active_simple_filter import ClientActiveFilter
from app.shopify_partner.jobs.register import register_sp_keys_setting
from app.shopify_partner.models import Setting, ShopifyPartnerOauthClientRegister, OauthTokenRequest
from app.shopify_partner.static_setting import SHOPIFY_PARTNER_STATIC_SETTING


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'secret', 'get_decrypt_secret', 'scope', 'redirect_url_oauth', 'web_redirect_url']

    def save_model(self, request, obj, form, change):
        # validate scope
        input_scope = obj.scope.split(",")
        invalid_scopes = [ele for ele in input_scope if ele not in SHOPIFY_PARTNER_STATIC_SETTING.available_scopes]
        if len(invalid_scopes):
            raise Exception("Invalid scopes: [%s]" % (','.join(invalid_scopes)))
        super(SettingAdmin, self).save_model(request, obj, form, change)


@admin.register(OauthTokenRequest)
class OauthTokenRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(ShopifyPartnerOauthClientRegister)
class ShopifyPartnerOauthClientRegisterAdmin(admin.ModelAdmin):
    list_display = ["client", "enabled"]
    list_filter = ['client', "enabled"]

    actions = ["register_ac"]

    def register_ac(self, request, queryset):
        client_ids = [str(ele.client_id) for ele in queryset]
        register_sp_keys_setting(client_ids)

    register_ac.short_description = "Register AC"
