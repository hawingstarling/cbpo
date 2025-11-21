class FlatSqlGeneratorInterface:

    def build_flat_query(self, *args, **kwargs):
        raise NotImplementedError

    def build_flat_query_schema_table(self, *args, **kwargs):
        raise NotImplementedError

    def build_flat_query_insert_table(self, *args, **kwargs):
        raise NotImplementedError

    def build_sql_do_update_set_by_conflict(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_for_number_sync_rows(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_for_number_flatten_rows(self, *args, **kwargs):
        raise NotImplementedError

    def build_revert_dirty_query(self, *args, **kwargs):
        raise NotImplementedError

    def build_sql_to_check_flatten_exists(self, *args, **kwargs):
        raise NotImplementedError

    def build_sql_to_drop_flatten(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_truncate_flatten(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_delete_old_docs(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_unique_index_flatten(self, *args, **kwargs):
        raise NotImplementedError

    def build_query_indexes_flatten(self, *args, **kwargs):
        raise NotImplementedError

    def build_properties_mapping_source(self, *args, **kwargs):
        raise NotImplementedError

    def build_flat_query_insert_segment_table(self, *args, **kwargs):
        raise NotImplementedError
