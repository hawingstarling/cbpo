from django.contrib import admin

# from app.core.admin.client_active_simple_filter import ClientActiveFilter
from app.selling_partner.models import Setting, OauthTokenRequest, SPOauthClientRegister, SPReportCategory, \
    SPReportType, SPReportClient, AppSetting


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['aws_oauth_consent_url', 'aws_oauth_access_token_url', 'created', 'modified']


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ['aws_default_region', 'aws_role_arn', 'spapi_app_id', 'amz_lwa_client_id', 'amz_lwa_client_secret',
                    'created', 'modified']


@admin.register(OauthTokenRequest)
class OauthTokenRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'state', 'spapi_oauth_code', 'selling_partner_id', 'created', 'modified']
    search_fields = ['state', 'spapi_oauth_code', 'selling_partner_id']
    ordering = ['-created']


@admin.register(SPOauthClientRegister)
class SPOauthClientRegisterAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'oauth_token_request', 'latest', 'created', 'modified']
    search_fields = ['oauth_token_request__spapi_oauth_code']
    list_filter = ['client', 'latest']
    ordering = ['-created']


@admin.register(SPReportCategory)
class SPReportCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'name', 'sort', 'created', 'modified']
    search_fields = ['name']
    list_filter = ['sort']
    ordering = ['sort']


@admin.register(SPReportType)
class SPReportTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'name', 'value', 'sort', 'created', 'modified']
    search_fields = ['name']
    list_filter = ['sort', 'category']
    ordering = ['sort']


@admin.register(SPReportClient)
class SPReportClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_type', 'ac_report_id', 'batch_ids', 'status', 'retry', 'date_range_covered_start',
                    'date_range_covered_end', 'created', 'modified']
    search_fields = ['id', 'ac_report_id']
    list_filter = ['client', 'status']
    ordering = ['-created']
