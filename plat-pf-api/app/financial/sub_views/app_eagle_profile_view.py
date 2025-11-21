from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from app.financial.models import AppEagleProfile
from app.financial.permissions.base import JwtTokenPermission
from app.financial.services.exports.schema import ExportSchema
from app.financial.services.postgres_fulltext_search import ISortConfigPostgresFulltextSearch
from app.financial.sub_serializers.app_eagle_profile_serializer import AppEagleProfileSerializer
from app.core.sub_serializers.base_serializer import ExportResponseSerializer


class ListAppEagleProfileBaseView(generics.GenericAPIView):
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        base_filter = Q(client_id=client_id)

        sort_field = self.request.query_params.get('sort_field')
        if sort_field:
            sort_direction = self.request.query_params.get('sort_direction')
            sort = [ISortConfigPostgresFulltextSearch(field_name=sort_field, direction=sort_direction)]
        else:
            sort = [ISortConfigPostgresFulltextSearch(field_name='created', direction='desc')]

        search_keyword = self.request.query_params.get('keyword')
        if search_keyword:
            base_filter = base_filter & (
                    Q(profile_id__icontains=search_keyword) | Q(profile_name__icontains=search_keyword) | Q(
                profile_id_link__icontains=search_keyword))
        #
        order_by = [item.output_str_sorting for item in sort]
        res_query_set = AppEagleProfile.objects.tenant_db_for(client_id).filter(base_filter).order_by(*order_by)
        return res_query_set


class ListAppEagleProfileView(generics.ListAPIView, ListAppEagleProfileBaseView):
    serializer_class = AppEagleProfileSerializer
    permission_classes = (JwtTokenPermission,)

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    sort_field = openapi.Parameter('sort_field', in_=openapi.IN_QUERY,
                                   description="""sort_field""",
                                   type=openapi.TYPE_STRING)
    sort_direction = openapi.Parameter('sort_direction', in_=openapi.IN_QUERY,
                                       description="""desc or asc""",
                                       type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[keyword, sort_field, sort_direction])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDeleteAppEagleProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppEagleProfileSerializer
    permission_classes = [JwtTokenPermission]
    queryset = AppEagleProfile.objects.all()

    def get_queryset(self):
        query_set = AppEagleProfile.objects.tenant_db_for(self.kwargs["client_id"]).all()
        return query_set


class ExportAppEagleProfileView(ListAppEagleProfileBaseView):
    permission_classes = [JwtTokenPermission]

    keyword = openapi.Parameter('keyword', in_=openapi.IN_QUERY,
                                description="""Search""",
                                type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        operation_description='Search Profile ID, Profile Name, Profile ID link',
        manual_parameters=[keyword], responses={status.HTTP_200_OK: ExportResponseSerializer})
    def get(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        columns = {
            'profile_id': 'Profile ID',
            'profile_name': 'Profile Name'
        }
        export_schema = ExportSchema(client_id=self.kwargs['client_id'], columns=columns, queryset=query_set,
                                     category='app_eagle_profile')
        file_url = export_schema.processing()
        return Response(status=HTTP_200_OK, data={'file_url': file_url})
