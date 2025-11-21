from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from app.core.context import AppContext
from app.financial.models import Brand, BrandSetting
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.activity import ActivityService
from app.financial.services.exports.schema import ExportSchema
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch
from app.core.sub_serializers.base_serializer import ExportResponseSerializer
from app.financial.sub_serializers.brand_serializer import BrandSerializer
from app.job.utils.helper import register
from app.job.utils.variable import SYNC_DATA_SOURCE_CATEGORY, MODE_RUN_SEQUENTIALLY


class ListBrandBaseView(generics.GenericAPIView):
    permission_classes = [JwtTokenPermission]
    serializer_class = BrandSerializer

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        base_filter = Q(client_id=client_id)

        sort_field = self.request.query_params.get('sort_field')
        if sort_field:
            sort_direction = self.request.query_params.get('sort_direction')
            sort = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
        else:
            sort = [ISortConfigPostgresFulltextSearch(field_name='created', direction='desc')]

        search_keyword = self.request.query_params.get('search')
        if search_keyword:
            base_filter = base_filter & (
                    Q(name__icontains=search_keyword) | Q(supplier_name__icontains=search_keyword) | Q(
                edi__icontains=search_keyword))

        is_obsolete = self.request.query_params.get('is_obsolete', None)
        if is_obsolete is not None:
            if is_obsolete == '1':
                base_filter &= Q(is_obsolete=True)
            if is_obsolete == '0':
                base_filter &= Q(is_obsolete=False)
        #
        order_by = [item.output_str_sorting for item in sort]
        res_query_set = Brand.objects.tenant_db_for(client_id).filter(base_filter).order_by(*order_by)
        return res_query_set


class ListBrandView(generics.ListAPIView, ListBrandBaseView):
    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search""",
                               type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    is_obsolete = openapi.Parameter('is_obsolete', in_=openapi.IN_QUERY,
                                    description="""Filter is_obsolete""",
                                    type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[search, is_obsolete, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDeleteBrandView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [JwtTokenPermission]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def get_queryset(self):
        query_set = Brand.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set

    def delete(self, request, *args, **kwargs):
        client_id = self.kwargs["client_id"]
        brand_id = self.kwargs["pk"]
        user_id = AppContext.instance().user_id
        res = super().delete(request, *args, **kwargs)
        # NOTED: The IT Team confirm keep sale items keep old value, don't be reset
        # data = dict(
        #     name=f"reset_data_brand_{brand_id}",
        #     job_name="app.financial.jobs.settings.handler_delete_brand_setting",
        #     module="app.financial.jobs.settings",
        #     method="handler_delete_brand_setting",
        #     time_limit=None,
        #     meta=dict(client_id=client_id, brand_id=brand_id, user_id=user_id)
        # )
        BrandSetting.objects.tenant_db_for(client_id).filter(brand_id=brand_id).delete()
        transaction.on_commit(
            lambda: {
                ActivityService(client_id=client_id, user_id=user_id).create_activity_delete_brand_data(brand_id),
                # register(category=SYNC_DATA_SOURCE_CATEGORY, client_id=client_id, mode_run=MODE_RUN_SEQUENTIALLY,
                #          **data)
            }
        )
        return res


class ExportBrandView(ListBrandBaseView):
    search = openapi.Parameter('search', in_=openapi.IN_QUERY,
                               description="""Search""",
                               type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        operation_description='Search Name, Supplier Name, EDI',
        manual_parameters=[search], responses={status.HTTP_200_OK: ExportResponseSerializer})
    def get(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        columns = {
            'name': 'Name',
            'supplier_name': 'Supplier Name',
            'is_obsolete': 'Is Obsolete',
            'acquired_date': 'Acquired Date',
        }
        export_schema = ExportSchema(client_id=self.kwargs['client_id'], columns=columns, queryset=query_set,
                                     category='brands')
        file_url = export_schema.processing()
        return Response(status=HTTP_200_OK, data={'file_url': file_url})
