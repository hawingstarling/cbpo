import logging
from django.contrib import admin
from django.db import DEFAULT_DB_ALIAS

from app.database.helper import get_connection_workspace

logger = logging.getLogger(__name__)


class TenantDBForModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        try:
            client_id = obj.client_id
        except Exception as ex:
            client_id = None
        client_db = get_connection_workspace(client_id)
        obj.save(using=client_db)

    def delete_model(self, request, obj):
        try:
            client_id = obj.client_id
        except Exception as ex:
            client_id = None
        client_db = get_connection_workspace(client_id)
        #
        self.delete_related_objects(request, obj)
        #
        obj.delete(using=client_db)

    def delete_queryset(self, request, queryset):
        #
        try:
            for obj in queryset:
                self.delete_related_objects(request, obj)
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][delete_queryset][{self.model.__name__}] {ex}")
        #
        super().delete_queryset(request, queryset)

    def delete_related_objects(self, request, obj):
        try:
            #
            for relation in self.model._meta.related_objects:
                relation_model = relation.related_model
                try:
                    field_relation = f"{relation.field.name}_id"
                    cond = {field_relation: obj.pk}
                    relation_model.objects.tenant_db_for(
                        obj.client_id).filter(**cond).delete()
                    # logger.info(
                    #     f"[{self.__class__.__name__}][delete_related_objects][{self.model.__name__}][{relation_model.__name__}] {cond}")
                except Exception as ex:
                    logger.error(
                        f"[{self.__class__.__name__}][delete_related_objects][{self.model.__name__}][{relation_model.__name__}] {ex}")
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][delete_related_objects][{self.model.__name__}] {ex}")

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

    def get_queryset(self, request):
        try:
            client_id = self.get_client_id_request(request)
            qs = self.model._default_manager.tenant_db_for(client_id).get_queryset()
            ordering = self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}][get_queryset] {ex}")
            self.model._default_manager.tenant_db_for(None)
        return super().get_queryset(request).using(DEFAULT_DB_ALIAS)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        try:
            client_id = self.get_client_id_request(request)
            client_db = get_connection_workspace(client_id)
            kwargs.update({'using': client_db})
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}][formfield_for_foreignkey] {ex}")
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        try:
            client_id = self.get_client_id_request(request)
            client_db = get_connection_workspace(client_id)
            kwargs.update({'using': client_db})
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}][formfield_for_manytomany] {ex}")
            pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)
