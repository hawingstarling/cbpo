import logging
from app.database.helper import get_connection_workspace
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from app.es.helper import get_es_sources_configs
from app.financial.services.api_data_source_centre import ApiCentreContainer
from app.financial.services.data_source import DataSource
from app.financial.services.utils.common import get_flatten_source_name
from app.financial.variable.data_flatten_variable import FLATTEN_SALE_ITEM_KEY, FLATTEN_ES_SOURCE
from config.settings.common import DS_TOKEN

logger = logging.getLogger(__name__)


def get_es_service(client_id: str, type_flatten: str, properties_settings: dict):
    try:
        es_sources_configs = get_es_sources_configs()
        assert type_flatten in es_sources_configs.keys(), f"{type_flatten} not config ES source"
        return get_es_sources_configs()[type_flatten](
            client_id=client_id, type_flatten=type_flatten,
            properties_settings=properties_settings
        )
    except Exception as ex:
        logger.error(
            f"[{__name__}][get_es_service] Error {ex}"
        )
        return None


def get_analysis_es_service(client_id: str):
    from app.financial.sql_generator.flat_sql_generator_container import SqlGeneratorContainer
    return get_es_service(
        client_id=client_id,
        type_flatten=FLATTEN_SALE_ITEM_KEY,
        properties_settings=SqlGeneratorContainer.flat_sale_items().build_properties_mapping_source(FLATTEN_ES_SOURCE)
    )


def bulk_sync(client_id, new_models, key_fields, filters, batch_size=None, fields=None, skip_creates=False,
              skip_updates=False, skip_deletes=False, savepoint: bool = True):
    """ Combine bulk create, update, and delete.  Make the DB match a set of in-memory objects.

    `new_models`: Django ORM objects that are the desired state.  They may or may not have `id` set.
    `key_fields`: Identifying attribute name(s) to match up `new_models` items with database rows.  If a foreign key
            is being used as a key field, be sure to pass the `fieldname_id` rather than the `fieldname`.
    `filters`: Q() filters specifying the subset of the database to work in.  Use `None` or `[]` if you want to sync against the entire table.
    `batch_size`: passes through to Django `bulk_create.batch_size` and `bulk_update.batch_size`, and controls
            how many objects are created/updated per SQL query.
    `fields`: (optional) list of fields to update. If not set, will sync all fields that are editable and not auto-created.
    `skip_creates`: If truthy, will not perform any object creations needed to fully sync. Defaults to not skip.
    `skip_updates`: If truthy, will not perform any object updates needed to fully sync. Defaults to not skip.
    `skip_deletes`: If truthy, will not perform any object deletions needed to fully sync. Defaults to not skip.
    """
    assert client_id is not None, "Client ID is not empty"
    client_db = get_connection_workspace(client_id)
    db_class = new_models[0].__class__

    if fields is None:
        # Get a list of fields that aren't PKs and aren't editable (e.g. auto_add_now) for bulk_update
        fields = [field.name
                  for field in db_class._meta.fields
                  if not field.primary_key and not field.auto_created and field.editable]

    with transaction.atomic(using=client_db, savepoint=savepoint):
        try:
            objs = db_class.all_objects.tenant_db_for(client_db).all()
        except Exception as ex:
            objs = db_class.all_objects.db_manager(using=client_db).all()
        if filters:
            objs = objs.filter(filters)
        objs = objs.only("pk", *key_fields).select_for_update()

        def get_key(obj):
            return tuple(getattr(obj, k) for k in key_fields)

        obj_dict = {get_key(obj): obj for obj in objs}

        new_objs = []
        existing_objs = []
        for new_obj in new_models:
            new_obj._state.db = client_db
            old_obj = obj_dict.pop(get_key(new_obj), None)
            if old_obj is None:
                # This is a new object, so create it.
                # Make sure the primary key field is clear.
                new_obj.pk = None
                new_objs.append(new_obj)
            else:
                new_obj.id = old_obj.id
                existing_objs.append(new_obj)

        if not skip_creates:
            try:
                db_class.objects.tenant_db_for(client_id).bulk_create(new_objs, batch_size=batch_size)
            except Exception as ex:
                db_class.objects.db_manager(using=client_db).bulk_create(new_objs, batch_size=batch_size)

        if not skip_updates:
            try:
                db_class.all_objects.tenant_db_for(client_id).bulk_update(existing_objs, fields=fields,
                                                                          batch_size=batch_size)
            except Exception as ex:
                db_class.all_objects.db_manager(using=client_db).bulk_update(existing_objs, fields=fields,
                                                                             batch_size=batch_size)

        if not skip_deletes:
            is_soft_delete = True
            try:
                db_class._meta.get_field('is_removed')
            except FieldDoesNotExist:
                is_soft_delete = False
            # delete stale objects
            if is_soft_delete:
                objs.filter(pk__in=[_.pk for _ in list(obj_dict.values())]).update(is_removed=True)
            else:
                objs.filter(pk__in=[_.pk for _ in list(obj_dict.values())]).delete()

        assert len(existing_objs) == len(new_models) - len(new_objs)

        stats = {
            "created": 0 if skip_creates else len(new_objs),
            "updated": 0 if skip_updates else (len(new_models) - len(new_objs)),
            "deleted": 0 if skip_deletes else len(obj_dict)
        }

        logger.info(
            "{}: {} created, {} updated, {} deleted.".format(
                db_class.__name__, stats["created"], stats["updated"], stats["deleted"]
            )
        )

    return {"stats": stats}


def get_analysis_3rd_party(client_id: str, source: str = FLATTEN_ES_SOURCE):
    data_source = DataSource(
        client_id=client_id,
        type_flatten=FLATTEN_SALE_ITEM_KEY,
        table=get_flatten_source_name(client_id),
        api_centre=ApiCentreContainer.data_source_central(),
        source=source,
        access_token=DS_TOKEN,
        token_type="DS_TOKEN"
    )
    return data_source
