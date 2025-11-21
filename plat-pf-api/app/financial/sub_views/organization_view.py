from django.db import DEFAULT_DB_ALIAS
from django.db.models import OuterRef, Exists, F, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from drf_yasg import openapi
from app.core.permissions.whilelist import SafeListPermission
from app.financial.models import Organization, ClientPortal
from app.financial.sub_serializers.organization_serializer import OrganizationSerializer, ClientSerializer, \
    ClientSettingSerializer
from app.shopify_partner.models import ShopifyPartnerOauthClientRegister


class OrganizationView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [SafeListPermission]

    def get_queryset(self):
        return Organization.objects.tenant_db_for(DEFAULT_DB_ALIAS) \
            .filter(clientportal__active=True) \
            .order_by('name')

    @swagger_auto_schema(tags=["Stats Reports"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrgClientView(generics.ListAPIView):
    serializer_class = ClientSerializer
    permission_classes = [SafeListPermission]

    def get_queryset(self):
        org_id = self.kwargs['id']
        cond = Q(active=True, organization_id=org_id)
        return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).order_by('name')

    @swagger_auto_schema(tags=["Stats Reports"])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrgClientSettingView(OrgClientView):
    serializer_class = ClientSettingSerializer

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search by value""",
                               type=openapi.TYPE_STRING)

    def get_queryset(self):
        recent_shopify = ShopifyPartnerOauthClientRegister.objects.filter(
            client=OuterRef('pk'),
            enabled=True
        )
        cond = Q(active=True)
        search = self.request.query_params.get('search')
        if search:
            cond &= (Q(name__icontains=search) | Q(organization__name__icontains=search))
        return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(cond).annotate(
            amazon=F('clientsettings__ac_spapi_enabled'),
            shopify=Exists(recent_shopify),
            cart_rover=F('clientsettings__ac_cart_rover_enabled'),
        ).order_by('name')

    @swagger_auto_schema(tags=["Stats Reports"], manual_parameters=[search])
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
