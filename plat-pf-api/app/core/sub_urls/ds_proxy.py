from django.urls import path
from django.conf import settings
from django.conf.urls import url
from app.core.proxy.ds import DSProxyView, PingDSProxyView

urlpatterns = [
    path('ping', PingDSProxyView.as_view(upstream=settings.URL_DS_SERVICE), name='ping-proxy-pf-to-ds'),
    url(r'(?P<path>.*)$', DSProxyView.as_view(upstream=settings.URL_DS_SERVICE), name='proxy-pf-to-ds'),
]
