from app.financial.sub_urls import (
    import_url, custom_url, client_url, activity_url, brand_setting_url, item_url, data_feed_url, shipping_invoice_url,
    app_eagle_profile_url, brand_url, alert_url, tag_url, export_url, top_product_performance_url, sale_by_sku_url,
    client_user_track_url, dashboard_url, cart_rover_url, organization_url, top_asins_url)

urlpatterns = import_url.urlpatterns \
              + custom_url.urlpatterns \
              + client_url.urlpatterns \
              + activity_url.urlpatterns \
              + brand_setting_url.urlpatterns \
              + item_url.urlpatterns \
              + data_feed_url.urlpatterns \
              + shipping_invoice_url.urlpatterns \
              + app_eagle_profile_url.urlpatterns \
              + brand_url.urlpatterns \
              + alert_url.urlpatterns \
              + tag_url.urlpatterns \
              + export_url.urlpatterns \
              + top_product_performance_url.urlpatterns \
              + sale_by_sku_url.urlpatterns \
              + client_user_track_url.urlpatterns \
              + dashboard_url.urlpatterns \
              + cart_rover_url.urlpatterns \
              + organization_url.urlpatterns \
              + top_asins_url.urlpatterns
