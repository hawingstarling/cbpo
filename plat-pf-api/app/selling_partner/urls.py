from app.selling_partner.sub_urls import setting_url, callback_url, token_url, report

urlpatterns = setting_url.urlpatterns + callback_url.urlpatterns + token_url.urlpatterns + report.urlpatterns
