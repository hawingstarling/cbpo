import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.financial.models import Activity
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.postgres_fulltext_search import PostgresFulltextSearch, ISortConfigPostgresFulltextSearch, \
    IFieldConfigPostgresFulltextSearch
from app.financial.sub_serializers.activity_serializer import ActivitySerializer

logger = logging.getLogger(__name__)


class ActivityListView(generics.ListAPIView):
    permission_classes = (JwtTokenPermission,)
    serializer_class = ActivitySerializer

    key = openapi.Parameter('key', in_=openapi.IN_QUERY,
                            description='Search by information (client name, user name, user email, action name, ...)',
                            type=openapi.TYPE_STRING)

    # priority is is in order of weight
    __config_search = [
        IFieldConfigPostgresFulltextSearch(field_name='user__username', weight='A'),
        IFieldConfigPostgresFulltextSearch(field_name='user__email', weight='A'),
        IFieldConfigPostgresFulltextSearch(field_name='user__first_name', weight='A'),
        IFieldConfigPostgresFulltextSearch(field_name='user__last_name', weight='A'),
        IFieldConfigPostgresFulltextSearch(field_name='action', weight='B'),
        IFieldConfigPostgresFulltextSearch(field_name='data', weight='C'),
    ]
    __sort_config = [ISortConfigPostgresFulltextSearch(field_name='created', direction='desc')]

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        key = self.request.query_params.get('key', None)
        if not key:
            return Activity.objects.tenant_db_for(client_id).filter(client_id=client_id).order_by('-created')
        res_1 = PostgresFulltextSearch(
            model_objects_manager=Activity.objects.tenant_db_for(client_id).filter(client_id=client_id),
            sort_config=self.__sort_config,
            fields_config=self.__config_search).search_rank_on_contain(key)
        res_2 = PostgresFulltextSearch(
            model_objects_manager=Activity.objects.tenant_db_for(client_id).filter(client_id=client_id),
            sort_config=self.__sort_config,
            fields_config=self.__config_search).search_rank_on_contain(key.replace(' ', '_'))
        return [*res_2, *[item for item in res_1 if item not in res_2]]

    @swagger_auto_schema(operation_description='Get list activity of Workspace', manual_parameters=[key])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
