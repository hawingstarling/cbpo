import logging
from django.contrib.admin import RelatedFieldListFilter
from django.db import DEFAULT_DB_ALIAS

from app.financial.models import ClientPortal

logger = logging.getLogger(__name__)


class ClientActiveFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return ClientPortal.objects.tenant_db_for(DEFAULT_DB_ALIAS).filter(active=True).values_list('id', 'name')

    def get_client_id_request(self, request):
        try:
            client_id = request.GET.get('client__id__exact', None)
            if not client_id:
                client_id = request.GET.get('_changelist_filters', None)
            if 'client__id__exact' in client_id:
                client_id = client_id.split('=')[1]
            return client_id
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}][get_client_id_request] {ex}")
            client_id = None
        return client_id

    def get_query_where_children(self, queryset):
        try:
            query = queryset.query

            def filter_lookups(child):
                return child.lhs.field.name != 'is_removed'

            return list(filter(filter_lookups, query.where.children))
        except Exception as ex:
            pass
        return queryset.query.where.children

    def queryset(self, request, queryset):
        try:
            client_id = self.get_client_id_request(request)
            children = self.get_query_where_children(queryset)
            queryset.model.objects.tenant_db_for(client_id).get_queryset()
            queryset.query.where.children = children
        except Exception as ex:
            logger.error(f"[{self.__class__.__name__}][queryset] {ex}")
        return super().queryset(request, queryset)
