from django.conf.urls import url
from django.urls import include, path

urlpatterns = [
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('healths', include('app.stat_report.sub_urls.health_url')),
    path('', include('app.financial.urls')),
    path('', include('app.selling_partner.urls')),
    path('', include('app.shopify_partner.urls')),
    path('', include('app.stat_report.urls')),
    path('', include('app.extensiv.urls')),
]
