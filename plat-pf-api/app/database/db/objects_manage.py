import logging
from django.db.utils import DEFAULT_DB_ALIAS
from model_utils.managers import SoftDeletableManager
from django.db.models import ForeignKey, ManyToOneRel, OneToOneRel, ManyToManyRel

from app.database.bulk_update.manager import BulkUpdateManager

logger = logging.getLogger(__name__)


class MultiDbTableManagerBase(BulkUpdateManager):
    db_table_default = None
    db_table_template = None
    db_table_relation_fields = []
    using_db_table_template = False

    def __init__(self):
        super().__init__()

        self.client_id = None
        self.client_id_tbl = None
        self.client_db = DEFAULT_DB_ALIAS

        if self.using_db_table_template:
            # validate db_table_name
            assert self.db_table_default is not None, f"[{self.__class__.__name__}] db_table_default is not defined"
            assert self.db_table_template is not None, f"[{self.__class__.__name__}] db_table_template is not defined"
            assert '{client_id_tbl}' in self.db_table_template, f"[{self.__class__.__name__}] `client_id_tbl` param not in db_table_template"

    def tenant_db_for(self, value: str):
        self.client_id = value
        #
        self.init_db_table_config()
        #
        return self

    def init_db_table_config(self):
        if self.client_id is not None:
            if self.client_id == DEFAULT_DB_ALIAS:
                self.client_db = DEFAULT_DB_ALIAS
            else:
                self.client_id = str(self.client_id)
                self.client_id_tbl = self.client_id.replace('-', '_')
                #
                try:
                    from app.database.helper import get_connection_workspace
                    self.client_db = get_connection_workspace(self.client_id)
                except Exception as ex:
                    # logger.error(f"[{self.__class__}][init_db_table_config] {ex}")
                    self.client_db = DEFAULT_DB_ALIAS
        else:
            self.client_id_tbl = None
            self.client_db = DEFAULT_DB_ALIAS
        self._db = self.client_db
        self.set_db_table_template()

    def set_cached_col(self, field, db_table: str):
        try:
            field.cached_col.alias = db_table
        except Exception as ex:
            # logger.error(f"[{self.__class__.__name__}][{self.client_id}][{self.db}][set_cached_col]  {ex}")
            pass

    def change_db_table_fields(self):
        for field in self.model._meta.get_fields(include_hidden=True):
            self.set_cached_col(field, self.model._meta.db_table)
            #
            rel_managed = False
            if type(field) in [ForeignKey, OneToOneRel, ManyToManyRel, ManyToOneRel]:
                field.related_model.objects._db = self._db
                if hasattr(field.related_model.objects, 'db_table_template') \
                        and field.related_model.objects.db_table_template is not None \
                        and self.client_id_tbl is not None:
                    rel_managed = True
                    ref_db_table = field.related_model.objects.db_table_template.format(
                        client_id_tbl=self.client_id_tbl)
                elif hasattr(field.related_model.objects, 'db_table_default') \
                        and field.related_model.objects.db_table_default is not None:
                    ref_db_table = field.related_model.objects.db_table_default
                else:
                    ref_db_table = field.related_model._meta.db_table
                #
                field.related_model._meta.managed = rel_managed
                field.related_model._meta.db_table = ref_db_table
                for field_rel in field.related_model._meta.fields:
                    self.set_cached_col(field_rel, field.related_model._meta.db_table)

    def set_db_table_template(self):
        try:
            #
            if self.using_db_table_template:
                if self.client_id:
                    db_table = self.db_table_template.format(client_id_tbl=self.client_id_tbl)
                    self.model._meta.managed = False
                else:
                    db_table = self.db_table_default
                    self.model._meta.managed = True
                self.model._meta.db_table = db_table
            #
            self.change_db_table_fields()
            #
        except Exception as ex:
            logger.error(
                f"[{self.__class__.__name__}][{self.client_id}][{self.db}][set_db_table_template]  {ex}")


class SoftDeleteMultiDbTableManagerBase(MultiDbTableManagerBase, SoftDeletableManager):
    pass
