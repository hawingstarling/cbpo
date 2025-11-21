class TblModelAbstract:

    @property
    def table_name(self):
        raise NotImplementedError

    @property
    def sql_schema_table(self):
        raise NotImplementedError

    @property
    def schema_alter_table(self):
        raise NotImplementedError
