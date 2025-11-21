from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from app.extensiv.models import COGSConflict
from app.extensiv.sub_serializers.cogs_conflict_serializer import ExtensivCOGsConflictSerializer
from app.extensiv.variables import ConflictStatus, COGSourceSystem
from app.financial.models import Channel
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch


class ExtensivCOGsConflictView(generics.ListAPIView):
    serializer_class = ExtensivCOGsConflictSerializer
    permission_classes = [JwtTokenPermission]

    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search""",
                               type=openapi.TYPE_STRING)

    channel_param = openapi.Parameter(
        'channel', in_=openapi.IN_QUERY,
        description="""Channel filter""",
        type=openapi.TYPE_STRING,
        # 👈 pulls enum values
        enum=[channel.name for channel in Channel.objects.all()]
    )

    used_cog_param = openapi.Parameter(
        'used_cog',
        in_=openapi.IN_QUERY,
        description="Used COG filter",
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in COGSourceSystem]  # 👈 pulls enum values
    )

    status_param = openapi.Parameter(
        'status',
        in_=openapi.IN_QUERY,
        description="Status filter",
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in ConflictStatus]  # 👈 pulls enum values
    )

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        channel = self.request.query_params.get('channel')
        search = self.request.query_params.get('search')
        used_cog = self.request.query_params.get('used_cog')
        status = self.request.query_params.get('status')
        cond = Q(client_id=client_id)

        if channel:
            cond &= Q(channel__name=channel)

        if used_cog:
            cond &= Q(used_cog=used_cog)

        if status:
            cond &= Q(status=status)

        if search:
            cond &= (Q(sku__icontains=search)
                     | Q(sale_ids__contains=[search])
                     | Q(note__icontains=search))

        # Sorting
        sort_field = self.request.query_params.get('sort_field')
        sort_direction = self.request.query_params.get(
            'sort_direction', 'desc')
        if sort_field:
            sort = [ISortConfigPostgresFulltextSearch(
                field_name=sort_field, direction=sort_direction)]
        else:
            sort = [ISortConfigPostgresFulltextSearch(
                field_name='created', direction=sort_direction)]
        order_by = [item.output_str_sorting for item in sort]
        queryset = COGSConflict.objects.tenant_db_for(client_id) \
            .filter(cond).order_by(*order_by)

        return queryset

    @swagger_auto_schema(operation_description='Get list widgets of dashboard',
                         manual_parameters=[search, channel_param, used_cog_param, status_param, sort_field,
                                            sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
