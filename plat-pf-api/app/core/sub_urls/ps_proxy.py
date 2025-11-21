from django.conf.urls import url
from django.conf import settings

from app.core.proxy.base import BaseCustomProxyView

urlpatterns = [
    url(r'(?P<path>.*)$', BaseCustomProxyView.as_view(upstream=settings.URL_PORTAL_SERVICE), name='proxy-pf-to-ps')
]