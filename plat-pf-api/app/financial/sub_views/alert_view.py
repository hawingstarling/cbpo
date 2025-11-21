from drf_yasg import openapi
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.core.context import AppContext
from app.financial.models import Alert
from app.financial.permissions.alert import DeleteAlertPermission
from app.financial.permissions.base import JwtTokenPermission
from app.financial.sub_serializers.alert_serializer import AlertSerializer


class ListCreateAlertView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [JwtTokenPermission]

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        base_filter = Q(client_id=client_id)
        search_keyword = self.request.query_params.get('keyword')
        if search_keyword:
            base_filter = base_filter & Q(name__icontains=search_keyword)
        query_set = Alert.objects.tenant_db_for(client_id).filter(base_filter).order_by('created')
        return query_set

    @swagger_auto_schema(manual_parameters=[keyword])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data['creator'] = AppContext.instance().user_id
        request.data['client'] = kwargs['client_id']
        request.data['last_refresh_rate'] = None
        request.data['last_throttling_period'] = None
        return super().post(request, *args, **kwargs)


class RetrieveUpdateDeleteAlertView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlertSerializer
    permission_classes = [JwtTokenPermission]

    def get_queryset(self):
        query_set = Alert.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    def get_permissions(self):
        if hasattr(self.request, 'method') and self.request.method.upper() in ["DELETE"]:
            self.permission_classes = [DeleteAlertPermission]
        return super().get_permissions()

    def put(self, request, *args, **kwargs):
        request.data['creator'] = AppContext.instance().user_id
        request.data['client'] = kwargs['client_id']
        return super().put(request, *args, **kwargs)
