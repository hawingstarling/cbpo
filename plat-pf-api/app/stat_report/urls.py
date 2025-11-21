from app.stat_report.sub_urls import healthy_client_url, event_url, server_url, sale_recent_url

urlpatterns = healthy_client_url.urlpatterns + event_url.urlpatterns + server_url.urlpatterns + \
              sale_recent_url.urlpatterns
