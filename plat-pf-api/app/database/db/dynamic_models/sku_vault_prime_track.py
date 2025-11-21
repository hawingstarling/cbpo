from ..objects_manage import MultiDbTableManagerBase, SoftDeleteMultiDbTableManagerBase
from ...variable.schema_tables.financial import DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT, \
    DB_TABLE_SKU_VAULT_PRIME_TRACK_TEMPLATE


class SKUVaultPrimeTrackMultiTblManager(MultiDbTableManagerBase):
    db_table_default = DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT
    db_table_template = DB_TABLE_SKU_VAULT_PRIME_TRACK_TEMPLATE
    using_db_table_template = True


class SKUVaultPrimeTrackSoftDeleteMultiTblManager(SoftDeleteMultiDbTableManagerBase):
    db_table_default = DB_TABLE_SKU_VAULT_PRIME_TRACK_DEFAULT
    db_table_template = DB_TABLE_SKU_VAULT_PRIME_TRACK_TEMPLATE
    using_db_table_template = True