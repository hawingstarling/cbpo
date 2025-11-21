"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import path, include
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
# drf_yasg
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

schema_view = get_schema_view(
    openapi.Info(
        title="PORTAL API",
        default_version='v1',
        description="CBPO Portal API",
        contact=openapi.Contact(email="no-reply@hdwebsoft.com"),
        license=openapi.License(name="CBPO Portal License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


class Index(TemplateView):

    def get(self, request, *args, **kwargs):
        template = get_template('healthz.html')
        app_version = settings.APP_VERSION
        return HttpResponse(template.render({'app_version': app_version}, request))


class HealthzCheckView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(status=HTTP_200_OK)


urlpatterns = [
    path('', Index.as_view(), name='homepage-portal-api'),
    path('healthz/', HealthzCheckView.as_view(), name='healthz'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('v1/', include('config.api')),
]

handler500 = 'rest_framework.exceptions.server_error'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
